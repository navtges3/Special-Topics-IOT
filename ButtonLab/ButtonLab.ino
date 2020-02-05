#define BUTTON  4
#define LED     5

int buttonLastState = LOW;
int LED_State = LOW;

void setup() {
  // put your setup code here, to run once:
  pinMode(LED, OUTPUT);
  pinMode(BUTTON, INPUT);
 }

void loop() {
  // put your main code here, to run repeatedly:
  int val = digitalRead(BUTTON);

  if(val == LOW && buttonLastState == HIGH) {
    if(LED_State == LOW){
      LED_State = HIGH;  
    }
    else {
      LED_State = LOW;
    }
    digitalWrite(LED, LED_State);
  }
  buttonLastState = val;
}
