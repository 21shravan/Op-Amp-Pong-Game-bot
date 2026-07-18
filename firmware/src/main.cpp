#include <Arduino.h>

String incoming = "";

void setup()
{
  Serial.begin(115200);
  pinMode(34, INPUT);
}

void loop()
{
    if (Serial.available())
    {
        incoming = Serial.readStringUntil('\n');
        incoming.trim();

        int commaIndex = incoming.indexOf(',');
        int val1 = 0;
        int val2 = 0;

        if (commaIndex >= 0)
        {
            val1 = incoming.substring(0, commaIndex).toInt();
            val2 = incoming.substring(commaIndex + 1).toInt();
        }
        else
        {
            val1 = incoming.toInt();
        }

        val1 = constrain(val1, 0, 255);
        val2 = constrain(val2, 0, 255);

        dacWrite(25, val1);
        dacWrite(26, val2);

        delayMicroseconds(100);

        int digitalState = digitalRead(34);
        Serial.println(digitalState == HIGH ? "1" : "0");
    }
}
