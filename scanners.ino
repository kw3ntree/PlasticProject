#include <BH1750.h>
#include <Wire.h>

BH1750 lightMeter(0x23);

#define p_resistor A0
String container = "";
String id = "@"; //중앙 컴퓨터로 가는 모든 실질적 데이터들은 시작값으로 'id'를 가진다.


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  Wire.begin();
  if (!lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)){
      Serial.println(F("Error initialising BH1750"));
    }
  
  pinMode(p_resistor, INPUT);  
}

void loop() {
  // put your main code here, to run repeatedly:
  
  if (Serial.available() >0){
    if(phase1_observer()){
      Serial.println(id + "stop");//컨베이어밸트로 stop명령 전송
      float content1 = phase1(); //센서값 측정
      Serial.println(id + "start"); //측정완료 후 밸트 다시 진행
      
      container = id + String(content1) + "/"; //container에 센서값 저장
    }
    
    if(phase2_observer()){
      Serial.println(id + "stop");//컨베이어밸트로 stop명령 전송
      float content2 = phase2();
      Serial.println(id + "start"); //측정완료 후 밸트 다시 진행
      
      container = container + String(content2); 

      Serial.println(container); //디버깅 및 분석용 데이터 전송
    }
    
  }
}


bool phase1_observer(){
  float criterion = 500.0;
  bool state = false;
  float data = analogRead(p_resistor);
  if(data >criterion){state = true;}
  
  return state;
}
bool phase2_observer(){
  float criterion = 500.0;
  bool state = false;
  if (lightMeter.measurementReady()) {
    float lux = lightMeter.readLightLevel();
    if(lux > criterion){state = true;}
  }
  return state;
}

float phase1(){
  float current = 0.0;
  float cabinet[] = {0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0};
  float data_stream = analogRead(p_resistor);

  float max, min = cabinet[0];

  float criterion = 500.0;
  //센서 값 리스트에 할당
  for(int i=0; i<10; i++){
    cabinet[i] = data_stream;
    delay(100);
  }//배열 중 최대, 최소 분류
  for(int c=0; c<10; c++){
    if(cabinet[c] > max){max = cabinet[c];}
    else if(cabinet[c] < min){min = cabinet[c];}
  }
  //측정 최대값이 기준치 이상이면 해당 최대값을 현재값으로 지정하고 반환
  if(max > criterion){current = max;}
  return(current);
}
  

float phase2(){
  float current = 0.0;
  float cabinet[] = {0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0};
  float max, min = cabinet[0];
  float criterion = 500.0;
  
  if (lightMeter.measurementReady()) {
    float lux = lightMeter.readLightLevel();
    for(int i=0; i<10; i++){
      cabinet[i] = lux;
      delay(100);
      }//배열 중 최대, 최소 분류
    for(int c=0; c<10; c++){
      if(cabinet[c] > max){max = cabinet[c];}
      else if(cabinet[c] < min){min = cabinet[c];}
      }
    /** 모니터링
    Serial.print("Light: ");
    Serial.print(lux);
    Serial.println(" lx");
    */
  }
  if(max > criterion){current = max;}
  return(current);
}
