
# 🏓 Pong AI using ESP32 + Analog Circuit

A real-time Pong game where the **AI paddle is controlled by an analog electronic circuit** instead of software logic.

This project demonstrates the integration of:
- 🎮 Python (Pygame)
- ⚡ ESP32 (real-time communication)
- 🔌 Analog electronics (LM324 comparator-based decision system)

---

## 🚀 Project Overview

In this project:

- The **Python game** sends the ball and paddle position to ESP32.
- The **ESP32 converts these positions into analog voltages (PWM)**.
- An **LM324-based analog circuit compares signals** to decide:
  - Move paddle **UP**
  - Move paddle **DOWN**
- The decision is sent back to Python → controlling the AI paddle.

👉 The AI is **purely hardware-based**, not software.

---

## 🧠 System Architecture


Python Game
↓ (Serial: ball_y, paddle_y)
ESP32
↓ (PWM signals)
Analog Circuit (LM324 Comparator)
↓ (Decision signal)
ESP32
↓ (Serial: 0 or 1)
Python Game (AI Paddle moves)

````

---

## ⚙️ Features

- 🎮 Real-time Pong game using Pygame
- ⚡ Hardware-based AI (no software logic for opponent)
- 🔁 Bidirectional serial communication
- 📊 Debug overlay with FPS and live values
- 💡 Optional LED indicator for circuit decisions

---

## 🛠️ Hardware Requirements

- ESP32
- LM324 Op-Amp IC
- Resistors
- Breadboard + wires
- LED (optional for debug)
- USB cable

---

## 🔌 Circuit Description

The analog circuit works as a **comparator system**:

- Input 1 → Ball position (voltage from ESP32 PWM)
- Input 2 → Paddle position (voltage from ESP32 PWM)
- Output:
  - HIGH → Move paddle UP
  - LOW → Move paddle DOWN

⚠️ Note:
- Pull-up resistors are required for stable output
- LM324 output is not rail-to-rail at 3.3V

---

## 💻 Software Setup

### 1. Install Python dependencies

```bash
pip install pygame pyserial
````

---

### 2. Run the Game

```bash
cd python
python pong_game.py
```

---

### 3. Upload ESP32 Code

* Open Arduino IDE
* Select ESP32 board
* Upload:

```
esp32/esp32_controller.ino
```

---

## 🔄 Serial Communication Protocol

### Python → ESP32

```
ball_y,paddle_y\n
```

### ESP32 → Python

```
1  → Move UP
0  → Move DOWN
```

---

## 🎯 Controls

| Key | Action    |
| --- | --------- |
| W   | Move Up   |
| S   | Move Down |

---

## 🧪 Debug Features

* FPS display
* Ball position
* Paddle position
* Serial communication logs

---

## ⚠️ Known Issues & Fixes

### 1. ESP32 always reads 0

✔ Fix: Use correct ADC pin (e.g., GPIO34)

---

### 2. Comparator output too low (~1.3V)

✔ Reason: LM324 not rail-to-rail
✔ Fix: Use pull-up resistor or buffer stage

---

### 3. LED disturbs output

✔ Fix: Use transistor buffer or ESP32 GPIO for LED

---

### 4. Paddle stuck at top/bottom

✔ Fix: Ensure proper serial synchronization

---

## 🔮 Future Improvements

* 🎯 Difficulty levels
* 🤖 Hybrid AI (hardware + ML)
* 🎨 Advanced graphics & effects
* 🔊 Sound effects
* 📡 Wireless version using WiFi

---

## 📚 Learning Outcomes

* Embedded systems + Python integration
* Real-time serial communication
* Analog vs Digital decision systems
* Hardware-software co-design

---
