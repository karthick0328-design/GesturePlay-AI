/**
 * GesturePlay AI — Cyber Racer 2D Canvas Mini-Game
 * Playable directly in browser with Hand Gestures or Keyboard
 */

class CyberRacerGame {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    // Virtual resolution
    this.width = 640;
    this.height = 480;
    this.canvas.width = this.width;
    this.canvas.height = this.height;

    // Game state
    this.state = 'IDLE'; // IDLE, PLAYING, GAMEOVER
    this.score = 0;
    this.highScore = parseInt(localStorage.getItem('gestureplay_highscore') || '0', 10);
    this.distance = 0;
    this.speed = 0;
    this.baseSpeed = 7;
    this.maxSpeed = 16;
    this.health = 3;
    this.maxHealth = 3;
    
    // Player ship
    this.player = {
      x: this.width / 2,
      y: this.height - 80,
      width: 44,
      height: 60,
      targetX: this.width / 2,
      jumpY: 0,
      isJumping: false,
      isShielded: false,
      shieldTimer: 0,
      tilt: 0
    };

    // Obstacles and collectibles
    this.obstacles = [];
    this.collectibles = [];
    this.particles = [];
    this.roadStars = [];
    this.spawnTimer = 0;
    this.itemTimer = 0;

    // Audio synthesizer
    this.audioCtx = null;

    // Keys currently pressed
    this.activeKeyAction = 'NONE';
    
    this.initRoadStars();
    this.setupKeyboardListeners();
    this.loop = this.loop.bind(this);
    requestAnimationFrame(this.loop);
  }

  initAudio() {
    if (!this.audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  playTone(freq, type, duration, vol = 0.1) {
    if (!this.audioCtx) return;
    try {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);
      gain.gain.setValueAtTime(vol, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + duration);
    } catch (e) {
      // Audio autoplay policy fallback
    }
  }

  initRoadStars() {
    this.roadStars = [];
    for (let i = 0; i < 40; i++) {
      this.roadStars.push({
        x: Math.random() * this.width,
        y: Math.random() * this.height,
        speed: 1 + Math.random() * 3,
        size: 1 + Math.random() * 2
      });
    }
  }

  start() {
    this.initAudio();
    this.state = 'PLAYING';
    this.score = 0;
    this.distance = 0;
    this.health = this.maxHealth;
    this.speed = this.baseSpeed;
    this.obstacles = [];
    this.collectibles = [];
    this.particles = [];
    this.player.x = this.width / 2;
    this.player.targetX = this.width / 2;
    this.player.jumpY = 0;
    this.player.isJumping = false;
    this.player.isShielded = false;

    // Hide overlay
    const overlay = document.getElementById('game-start-overlay');
    if (overlay) overlay.style.display = 'none';

    this.playTone(440, 'triangle', 0.2, 0.15);
    setTimeout(() => this.playTone(660, 'triangle', 0.3, 0.2), 120);
  }

  gameOver() {
    this.state = 'GAMEOVER';
    if (this.score > this.highScore) {
      this.highScore = this.score;
      localStorage.setItem('gestureplay_highscore', this.highScore.toString());
    }

    this.playTone(220, 'sawtooth', 0.4, 0.2);
    setTimeout(() => this.playTone(150, 'sawtooth', 0.6, 0.25), 200);

    const overlay = document.getElementById('game-start-overlay');
    if (overlay) {
      overlay.style.display = 'flex';
      overlay.innerHTML = `
        <h3>SYSTEM OVERHEAT</h3>
        <p>Final Score: <strong style="color:#06b6d4">${this.score}</strong> &bull; Distance: <strong>${Math.floor(this.distance)}m</strong></p>
        <button id="btn-restart-game" class="btn btn-accent">
          <i class="bi bi-arrow-repeat"></i> Play Again
        </button>
      `;
      document.getElementById('btn-restart-game').addEventListener('click', () => this.start());
    }
  }

  // Handle incoming gesture command
  handleGesture(gesture) {
    if (this.state !== 'PLAYING') return;

    // Highlight keycaps in UI
    const highlightKey = (id) => {
      document.querySelectorAll('.key-keycap').forEach(k => k.classList.remove('active'));
      const el = document.getElementById(id);
      if (el) el.classList.add('active');
    };

    switch (gesture) {
      case 'OPEN_PALM':
        // Accelerate (W)
        this.speed = Math.min(this.speed + 0.4, this.maxSpeed);
        this.activeKeyAction = 'W (Accelerate)';
        highlightKey('keycap-w');
        this.createThrustParticles();
        break;

      case 'FIST':
        // Brake / Shield (S)
        this.speed = Math.max(this.speed - 0.5, 3);
        this.player.isShielded = true;
        this.player.shieldTimer = 30;
        this.activeKeyAction = 'S (Brake / Shield)';
        highlightKey('keycap-s');
        break;

      case 'PALM_LEFT':
        // Steer Left (A)
        this.player.targetX = Math.max(100, this.player.targetX - 9);
        this.player.tilt = -0.3;
        this.activeKeyAction = 'A (Steer Left)';
        highlightKey('keycap-a');
        break;

      case 'PALM_RIGHT':
        // Steer Right (D)
        this.player.targetX = Math.min(this.width - 100, this.player.targetX + 9);
        this.player.tilt = 0.3;
        this.activeKeyAction = 'D (Steer Right)';
        highlightKey('keycap-d');
        break;

      case 'TWO_FINGERS':
        // Jump / Nitro (SPACE)
        if (!this.player.isJumping) {
          this.player.isJumping = true;
          this.player.jumpVelocity = 14;
          this.playTone(520, 'sine', 0.25, 0.15);
        }
        this.activeKeyAction = 'SPACE (Jump)';
        highlightKey('keycap-space');
        break;

      case 'NO_HAND':
      default:
        // Gradually normalize speed
        if (this.speed > this.baseSpeed) this.speed -= 0.15;
        this.player.tilt *= 0.85;
        this.activeKeyAction = 'IDLE';
        document.querySelectorAll('.key-keycap').forEach(k => k.classList.remove('active'));
        break;
    }
  }

  setupKeyboardListeners() {
    window.addEventListener('keydown', (e) => {
      if (this.state === 'IDLE' && (e.code === 'Space' || e.code === 'KeyW')) {
        this.start();
        return;
      }
      if (this.state !== 'PLAYING') return;

      switch (e.code) {
        case 'KeyW':
        case 'ArrowUp':
          this.handleGesture('OPEN_PALM');
          break;
        case 'KeyS':
        case 'ArrowDown':
          this.handleGesture('FIST');
          break;
        case 'KeyA':
        case 'ArrowLeft':
          this.handleGesture('PALM_LEFT');
          break;
        case 'KeyD':
        case 'ArrowRight':
          this.handleGesture('PALM_RIGHT');
          break;
        case 'Space':
          this.handleGesture('TWO_FINGERS');
          break;
      }
    });

    window.addEventListener('keyup', (e) => {
      if (['KeyW', 'KeyS', 'KeyA', 'KeyD', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Space'].includes(e.code)) {
        this.handleGesture('NO_HAND');
      }
    });
  }

  createThrustParticles() {
    for (let i = 0; i < 2; i++) {
      this.particles.push({
        x: this.player.x + (Math.random() - 0.5) * 16,
        y: this.player.y + 25 - this.player.jumpY,
        vx: (Math.random() - 0.5) * 2,
        vy: 4 + Math.random() * 4,
        color: Math.random() > 0.5 ? '#38bdf8' : '#818cf8',
        radius: 2 + Math.random() * 3,
        life: 1.0,
        decay: 0.05
      });
    }
  }

  update() {
    if (this.state !== 'PLAYING') return;

    // Advance distance and score
    this.distance += this.speed * 0.1;
    this.score += Math.round(this.speed * 0.2);

    // Smooth player movement
    this.player.x += (this.player.targetX - this.player.x) * 0.2;

    // Handle Jump physics
    if (this.player.isJumping) {
      this.player.jumpY += this.player.jumpVelocity;
      this.player.jumpVelocity -= 0.8;
      if (this.player.jumpY <= 0) {
        this.player.jumpY = 0;
        this.player.isJumping = false;
      }
    }

    // Shield cooldown
    if (this.player.shieldTimer > 0) {
      this.player.shieldTimer--;
      if (this.player.shieldTimer <= 0) this.player.isShielded = false;
    }

    // Spawn obstacles
    this.spawnTimer++;
    if (this.spawnTimer > Math.max(30, 80 - Math.floor(this.distance / 50))) {
      this.spawnTimer = 0;
      const laneX = 140 + Math.random() * (this.width - 280);
      this.obstacles.push({
        x: laneX,
        y: -40,
        width: 48,
        height: 28,
        color: '#f43f5e',
        speed: this.speed * 0.95
      });
    }

    // Spawn energy orbs (collectibles)
    this.itemTimer++;
    if (this.itemTimer > 60) {
      this.itemTimer = 0;
      this.collectibles.push({
        x: 140 + Math.random() * (this.width - 280),
        y: -30,
        radius: 12,
        color: '#10b981',
        speed: this.speed * 0.9
      });
    }

    // Update obstacles
    for (let i = this.obstacles.length - 1; i >= 0; i--) {
      const obs = this.obstacles[i];
      obs.y += obs.speed;

      // Collision with player
      if (!this.player.isJumping && 
          Math.abs(this.player.x - obs.x) < (this.player.width / 2 + obs.width / 2) &&
          Math.abs(this.player.y - obs.y) < (this.player.height / 2 + obs.height / 2)) {
        
        if (this.player.isShielded) {
          // Blocked by shield!
          this.playTone(350, 'square', 0.2, 0.2);
          this.obstacles.splice(i, 1);
          continue;
        }

        // Damage taken
        this.health--;
        this.playTone(180, 'sawtooth', 0.3, 0.25);
        this.obstacles.splice(i, 1);

        if (this.health <= 0) {
          this.gameOver();
          return;
        }
        continue;
      }

      if (obs.y > this.height + 50) {
        this.obstacles.splice(i, 1);
      }
    }

    // Update collectibles
    for (let i = this.collectibles.length - 1; i >= 0; i--) {
      const item = this.collectibles[i];
      item.y += item.speed;

      if (Math.abs(this.player.x - item.x) < 32 && Math.abs((this.player.y - this.player.jumpY) - item.y) < 32) {
        this.score += 250;
        this.playTone(880, 'sine', 0.15, 0.2);
        this.collectibles.splice(i, 1);
        continue;
      }

      if (item.y > this.height + 50) {
        this.collectibles.splice(i, 1);
      }
    }

    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= p.decay;
      if (p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }

    // Update starfield
    this.roadStars.forEach(s => {
      s.y += s.speed * (this.speed / 5);
      if (s.y > this.height) {
        s.y = 0;
        s.x = Math.random() * this.width;
      }
    });

    // Update game telemetry elements
    const scoreEl = document.getElementById('telemetry-game-score');
    if (scoreEl) scoreEl.innerText = this.score;

    const speedEl = document.getElementById('telemetry-game-speed');
    if (speedEl) speedEl.innerText = `${Math.round(this.speed * 12)} km/h`;

    const healthEl = document.getElementById('telemetry-game-health');
    if (healthEl) {
      healthEl.innerHTML = '❤️'.repeat(this.health) + '🖤'.repeat(Math.max(0, this.maxHealth - this.health));
    }
  }

  draw() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Cyber space background
    this.ctx.fillStyle = '#05070e';
    this.ctx.fillRect(0, 0, this.width, this.height);

    // Stars
    this.ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    this.roadStars.forEach(s => {
      this.ctx.fillRect(s.x, s.y, s.size, s.size * (1 + this.speed * 0.2));
    });

    // Cyber Highway Perspective
    this.drawHighway();

    // Collectibles (Energy Orbs)
    this.collectibles.forEach(item => {
      this.ctx.save();
      this.ctx.shadowColor = item.color;
      this.ctx.shadowBlur = 15;
      this.ctx.fillStyle = item.color;
      this.ctx.beginPath();
      this.ctx.arc(item.x, item.y, item.radius, 0, 2 * Math.PI);
      this.ctx.fill();
      this.ctx.restore();
    });

    // Obstacles
    this.obstacles.forEach(obs => {
      this.ctx.save();
      this.ctx.shadowColor = obs.color;
      this.ctx.shadowBlur = 12;
      this.ctx.fillStyle = obs.color;
      this.ctx.fillRect(obs.x - obs.width / 2, obs.y - obs.height / 2, obs.width, obs.height);
      // Warning stripes
      this.ctx.fillStyle = '#000';
      this.ctx.fillRect(obs.x - obs.width / 4, obs.y - obs.height / 2, 4, obs.height);
      this.ctx.fillRect(obs.x + obs.width / 8, obs.y - obs.height / 2, 4, obs.height);
      this.ctx.restore();
    });

    // Particles
    this.particles.forEach(p => {
      this.ctx.save();
      this.ctx.globalAlpha = p.life;
      this.ctx.fillStyle = p.color;
      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, p.radius, 0, 2 * Math.PI);
      this.ctx.fill();
      this.ctx.restore();
    });

    // Draw Player Cyber Ship
    this.drawPlayer();

    // In-game HUD
    this.drawHUD();
  }

  drawHighway() {
    const horizonY = 80;
    const roadTopW = 180;
    const roadBottomW = this.width - 80;

    // Road fill
    this.ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    this.ctx.beginPath();
    this.ctx.moveTo(this.width / 2 - roadTopW / 2, horizonY);
    this.ctx.lineTo(this.width / 2 + roadTopW / 2, horizonY);
    this.ctx.lineTo(this.width / 2 + roadBottomW / 2, this.height);
    this.ctx.lineTo(this.width / 2 - roadBottomW / 2, this.height);
    this.ctx.closePath();
    this.ctx.fill();

    // Road Neon Edges
    this.ctx.strokeStyle = '#06b6d4';
    this.ctx.lineWidth = 3;
    this.ctx.shadowColor = '#06b6d4';
    this.ctx.shadowBlur = 15;
    
    // Left edge
    this.ctx.beginPath();
    this.ctx.moveTo(this.width / 2 - roadTopW / 2, horizonY);
    this.ctx.lineTo(this.width / 2 - roadBottomW / 2, this.height);
    this.ctx.stroke();

    // Right edge
    this.ctx.beginPath();
    this.ctx.moveTo(this.width / 2 + roadTopW / 2, horizonY);
    this.ctx.lineTo(this.width / 2 + roadBottomW / 2, this.height);
    this.ctx.stroke();

    // Center divider lines
    this.ctx.shadowBlur = 0;
    this.ctx.strokeStyle = 'rgba(99, 102, 241, 0.5)';
    this.ctx.setLineDash([25, 25]);
    this.ctx.lineDashOffset = -this.distance * 10;
    this.ctx.beginPath();
    this.ctx.moveTo(this.width / 2, horizonY);
    this.ctx.lineTo(this.width / 2, this.height);
    this.ctx.stroke();
    this.ctx.setLineDash([]);
  }

  drawPlayer() {
    const px = this.player.x;
    const py = this.player.y - this.player.jumpY;

    this.ctx.save();
    this.ctx.translate(px, py);
    this.ctx.rotate(this.player.tilt);

    // Ship shadow when jumping
    if (this.player.isJumping) {
      this.ctx.save();
      this.ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
      this.ctx.beginPath();
      this.ctx.ellipse(0, this.player.jumpY + 15, 20, 8, 0, 0, 2 * Math.PI);
      this.ctx.fill();
      this.ctx.restore();
    }

    // Shield bubble
    if (this.player.isShielded) {
      this.ctx.save();
      this.ctx.strokeStyle = 'rgba(16, 185, 129, 0.8)';
      this.ctx.lineWidth = 3;
      this.ctx.shadowColor = '#10b981';
      this.ctx.shadowBlur = 20;
      this.ctx.beginPath();
      this.ctx.arc(0, 0, 36, 0, 2 * Math.PI);
      this.ctx.stroke();
      this.ctx.restore();
    }

    // Ship fuselage
    this.ctx.fillStyle = '#6366f1';
    this.ctx.strokeStyle = '#38bdf8';
    this.ctx.lineWidth = 2;
    this.ctx.shadowColor = '#6366f1';
    this.ctx.shadowBlur = 12;

    this.ctx.beginPath();
    this.ctx.moveTo(0, -25);
    this.ctx.lineTo(18, 18);
    this.ctx.lineTo(0, 10);
    this.ctx.lineTo(-18, 18);
    this.ctx.closePath();
    this.ctx.fill();
    this.ctx.stroke();

    // Cockpit glow
    this.ctx.fillStyle = '#38bdf8';
    this.ctx.beginPath();
    this.ctx.arc(0, -5, 5, 0, 2 * Math.PI);
    this.ctx.fill();

    // Thruster engine glow
    this.ctx.fillStyle = this.speed > this.baseSpeed ? '#f59e0b' : '#06b6d4';
    this.ctx.beginPath();
    this.ctx.moveTo(-6, 12);
    this.ctx.lineTo(6, 12);
    this.ctx.lineTo(0, 22 + Math.random() * (this.speed * 1.2));
    this.ctx.closePath();
    this.ctx.fill();

    this.ctx.restore();
  }

  drawHUD() {
    this.ctx.font = '600 13px "JetBrains Mono", monospace';
    this.ctx.fillStyle = '#94a3b8';
    this.ctx.fillText(`SCORE: ${this.score}`, 18, 28);
    this.ctx.fillText(`DIST: ${Math.floor(this.distance)}m`, 18, 48);

    this.ctx.textAlign = 'right';
    this.ctx.fillText(`SPEED: ${Math.round(this.speed * 12)} KM/H`, this.width - 18, 28);
    this.ctx.fillText(`HEALTH: ${'❤️'.repeat(this.health)}`, this.width - 18, 48);
    this.ctx.textAlign = 'left';
  }

  loop() {
    this.update();
    this.draw();
    requestAnimationFrame(this.loop);
  }
}

window.CyberRacerGame = CyberRacerGame;
