/**
 * GesturePlay AI — Real-Time Browser Hand Gesture Tracker
 * Replicates the Python OpenCV + MediaPipe pipeline in JavaScript
 */

class BrowserGestureTracker {
  constructor(options = {}) {
    this.videoElement = options.videoElement || document.getElementById('webcam-video');
    this.canvasElement = options.canvasElement || document.getElementById('vision-canvas');
    this.ctx = this.canvasElement ? this.canvasElement.getContext('2d') : null;
    
    // Stable frame history (matches Python deque(maxlen=4))
    this.stableFrames = options.stableFrames || 4;
    this.history = [];
    this.currentStableGesture = "NO_HAND";
    this.rawGesture = "NO_HAND";
    
    // Callbacks
    this.onGestureDetected = options.onGestureDetected || (() => {});
    this.onTelemetryUpdate = options.onTelemetryUpdate || (() => {});
    
    // Performance metrics
    this.lastFrameTime = performance.now();
    this.fps = 0;
    this.frameCount = 0;
    this.fpsTimer = performance.now();
    
    this.isRunning = false;
    this.camera = null;
    this.hands = null;
  }

  async initMediaPipe() {
    if (!window.Hands) {
      console.error("MediaPipe Hands library not loaded from CDN.");
      return false;
    }

    this.hands = new window.Hands({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });

    this.hands.setOptions({
      maxNumHands: 1,
      modelComplexity: 1,
      minDetectionConfidence: 0.65,
      minTrackingConfidence: 0.6
    });

    this.hands.onResults((results) => this.processResults(results));
    return true;
  }

  async startCamera() {
    if (this.isRunning) return;

    const initialized = await this.initMediaPipe();
    if (!initialized) throw new Error("Failed to initialize MediaPipe Hands.");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "user"
        },
        audio: false
      });

      this.videoElement.srcObject = stream;
      await this.videoElement.play();

      if (this.canvasElement) {
        this.canvasElement.width = this.videoElement.videoWidth || 640;
        this.canvasElement.height = this.videoElement.videoHeight || 480;
      }

      this.camera = new window.Camera(this.videoElement, {
        onFrame: async () => {
          if (this.isRunning && this.videoElement && this.videoElement.readyState >= 2) {
            await this.hands.send({ image: this.videoElement });
          }
        },
        width: 640,
        height: 480
      });

      await this.camera.start();
      this.isRunning = true;
      return true;
    } catch (err) {
      console.error("Webcam access error:", err);
      throw err;
    }
  }

  stopCamera() {
    if (!this.isRunning) return;
    this.isRunning = false;

    if (this.camera && typeof this.camera.stop === 'function') {
      this.camera.stop();
    }

    if (this.videoElement && this.videoElement.srcObject) {
      const tracks = this.videoElement.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      this.videoElement.srcObject = null;
    }

    if (this.ctx && this.canvasElement) {
      this.ctx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);
    }

    this.currentStableGesture = "NO_HAND";
    this.onGestureDetected("NO_HAND", null);
  }

  getDistance(p1, p2) {
    return Math.hypot(p1.x - p2.x, p1.y - p2.y);
  }

  analyzeFingers(landmarks) {
    const wrist = landmarks[0];
    const thumb_tip = landmarks[4];
    const thumb_ip = landmarks[3];
    const pinky_mcp = landmarks[17];

    // Thumb extension check relative to palm width
    const thumb_extended = this.getDistance(thumb_tip, pinky_mcp) > this.getDistance(thumb_ip, pinky_mcp);

    // Finger extensions: tip vs PIP joint distance to wrist
    const index_extended = this.getDistance(landmarks[8], wrist) > this.getDistance(landmarks[6], wrist);
    const middle_extended = this.getDistance(landmarks[12], wrist) > this.getDistance(landmarks[10], wrist);
    const ring_extended = this.getDistance(landmarks[16], wrist) > this.getDistance(landmarks[14], wrist);
    const pinky_extended = this.getDistance(landmarks[20], wrist) > this.getDistance(landmarks[18], wrist);

    return {
      thumb: thumb_extended,
      index: index_extended,
      middle: middle_extended,
      ring: ring_extended,
      pinky: pinky_extended
    };
  }

  calculateOrientation(landmarks) {
    const wrist = landmarks[0];
    const middle_mcp = landmarks[9];

    const dx = middle_mcp.x - wrist.x;
    const dy = middle_mcp.y - wrist.y;

    const angle = (Math.atan2(dy, dx) * 180) / Math.PI;

    let orientation = "CENTER";
    // -90 is upright. In mirrored feed, angle heuristics map to LEFT / RIGHT
    if (angle >= -60 && angle <= 60) {
      orientation = "RIGHT";
    } else if (angle >= 120 || angle <= -120) {
      orientation = "LEFT";
    }

    return { orientation, angle };
  }

  classifyRawGesture(landmarks) {
    const fingers = this.analyzeFingers(landmarks);
    const { orientation, angle } = this.calculateOrientation(landmarks);

    const extCount = (fingers.thumb ? 1 : 0) + 
                     (fingers.index ? 1 : 0) + 
                     (fingers.middle ? 1 : 0) + 
                     (fingers.ring ? 1 : 0) + 
                     (fingers.pinky ? 1 : 0);

    // Orientation steering check (prioritized if tilted left or right)
    if (orientation === "LEFT") return { gesture: "PALM_LEFT", fingers, orientation, angle };
    if (orientation === "RIGHT") return { gesture: "PALM_RIGHT", fingers, orientation, angle };

    // Fist check
    if (extCount === 0 || (extCount === 1 && fingers.thumb)) {
      return { gesture: "FIST", fingers, orientation, angle };
    }

    // Open Palm check
    if (extCount === 5 || (extCount === 4 && !fingers.thumb)) {
      return { gesture: "OPEN_PALM", fingers, orientation, angle };
    }

    // Two fingers (Jump / Boost)
    if (fingers.index && fingers.middle && !fingers.ring && !fingers.pinky) {
      return { gesture: "TWO_FINGERS", fingers, orientation, angle };
    }

    // Single finger (Action / Steer)
    if (fingers.index && !fingers.middle && !fingers.ring && !fingers.pinky) {
      return { gesture: "ONE_FINGER", fingers, orientation, angle };
    }

    return { gesture: "UNKNOWN", fingers, orientation, angle };
  }

  processResults(results) {
    // Measure FPS
    const now = performance.now();
    this.frameCount++;
    if (now - this.fpsTimer >= 1000) {
      this.fps = Math.round((this.frameCount * 1000) / (now - this.fpsTimer));
      this.frameCount = 0;
      this.fpsTimer = now;
    }

    if (!this.ctx || !this.canvasElement) return;

    this.ctx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      const landmarks = results.multiHandLandmarks[0];

      // Draw skeleton & landmarks
      this.drawHand(landmarks);

      // Classify gesture
      const analysis = this.classifyRawGesture(landmarks);
      this.rawGesture = analysis.gesture;

      // Temporal debouncing
      this.history.push(this.rawGesture);
      if (this.history.length > this.stableFrames) {
        this.history.shift();
      }

      if (this.history.length === this.stableFrames) {
        const isStable = this.history.every(g => g === this.rawGesture);
        if (isStable) {
          this.currentStableGesture = this.rawGesture;
        }
      }

      this.onGestureDetected(this.currentStableGesture, analysis);
      this.onTelemetryUpdate({
        fps: this.fps,
        gesture: this.currentStableGesture,
        rawGesture: this.rawGesture,
        angle: Math.round(analysis.angle),
        orientation: analysis.orientation,
        handDetected: true
      });
    } else {
      this.history.push("NO_HAND");
      if (this.history.length > this.stableFrames) this.history.shift();
      if (this.history.every(g => g === "NO_HAND")) {
        this.currentStableGesture = "NO_HAND";
      }

      this.onGestureDetected(this.currentStableGesture, null);
      this.onTelemetryUpdate({
        fps: this.fps,
        gesture: this.currentStableGesture,
        rawGesture: "NO_HAND",
        angle: 0,
        orientation: "NONE",
        handDetected: false
      });
    }
  }

  drawHand(landmarks) {
    const w = this.canvasElement.width;
    const h = this.canvasElement.height;

    // Connectors
    const connections = [
      [0,1],[1,2],[2,3],[3,4],
      [0,5],[5,6],[6,7],[7,8],
      [5,9],[9,10],[10,11],[11,12],
      [9,13],[13,14],[14,15],[15,16],
      [13,17],[17,18],[18,19],[19,20],[0,17]
    ];

    // Glow line style
    this.ctx.lineWidth = 3;
    this.ctx.strokeStyle = "rgba(6, 182, 212, 0.85)";
    this.ctx.shadowColor = "#06b6d4";
    this.ctx.shadowBlur = 10;

    connections.forEach(([i, j]) => {
      const p1 = landmarks[i];
      const p2 = landmarks[j];
      this.ctx.beginPath();
      this.ctx.moveTo(p1.x * w, p1.y * h);
      this.ctx.lineTo(p2.x * w, p2.y * h);
      this.ctx.stroke();
    });

    // Draw landmark joints
    this.ctx.shadowBlur = 0;
    landmarks.forEach((p, idx) => {
      this.ctx.beginPath();
      this.ctx.arc(p.x * w, p.y * h, idx % 4 === 0 ? 5 : 3.5, 0, 2 * Math.PI);
      if ([4, 8, 12, 16, 20].includes(idx)) {
        this.ctx.fillStyle = "#38bdf8"; // Tips in bright cyan
      } else if (idx === 0) {
        this.ctx.fillStyle = "#a855f7"; // Wrist in purple
      } else {
        this.ctx.fillStyle = "#ffffff";
      }
      this.ctx.fill();
    });
  }
}

window.BrowserGestureTracker = BrowserGestureTracker;
