String line = "";
int ballY = 0, paddleY = 0;

int ballVoltagePin = 23;
int paddleVoltagePin = 22;

int decisionPin = 33;

// PWM
const int freq = 5000;
const int resolution = 8;

unsigned long lastSend = 0;

void setup() {
  Serial.begin(115200);

  ledcAttach(ballVoltagePin, freq, resolution);
  ledcAttach(paddleVoltagePin, freq, resolution);
  pinMode(decisionPin, INPUT);   // add in setup()
}
void loop() {
  bool newLineReceived = false;
  
  // 1. NON-BLOCKING READ: Find a complete frame from Python
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      int comma = line.indexOf(',');
      if (comma > 0) {
        // Successfully parsed a new frame
        ballY = line.substring(0, comma).toInt();
        paddleY = line.substring(comma + 1).toInt();
        newLineReceived = true; // Signal that we received new data
      }
      line = ""; // Reset line buffer for the next frame
    } 
    else {
      line += c; // Build the current line
    }
  }

  // 2. ONLY PROCESS AND RESPOND IF A NEW FRAME WAS RECEIVED
  if (newLineReceived) {
    // ----------- OUTPUT PWM TO CIRCUIT ----------------------
    // Map the 0-400 pixel range to 0-255 PWM range
    int ballPWM = map(ballY, 0, 500, 0, 255);
    int paddlePWM = map(paddleY, 0, 500, 0, 255);

    ledcWrite(ballVoltagePin, ballPWM);
    ledcWrite(paddleVoltagePin, paddlePWM);

    // Give the comparator a tiny moment to stabilize
    delay(1); 

    // ----------- READ COMPARATOR AND RESPOND ----------------
    int decision = digitalRead(decisionPin);
    // Send the decision (0 or 1) back to Python
    Serial.println(decision);
  }
}