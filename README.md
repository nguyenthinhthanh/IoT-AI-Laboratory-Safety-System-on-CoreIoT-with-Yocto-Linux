# IoT System with AI and Yocto Linux for Laboratory Environment and Safety Monitoring Based on CoreIoT Platform

## 1. Introduction

This repository contains the **source code** of an **AI-integrated IoT system for laboratory environment and safety monitoring**, developed on top of the **CoreIoT platform**.

The system is designed to run on **embedded Linux devices** and focuses on **real-time data acquisition, edge AI inference, and centralized monitoring** for laboratory safety applications.

## 2. Project Scope

The project addresses two main aspects of laboratory safety:

### Environmental Monitoring

- Temperature
- Humidity
- CO₂ concentration
- VOC levels

(using industrial sensors via **Modbus RS-485**)

### Human-Centered Safety Monitoring

- People counting using camera input
- Fatigue or inattention detection using AI models
- (Optional) mask detection and overcrowding monitoring

## 3. System Architecture

```
+-----------------------------+
| Industrial Sensors (RS-485) |
|  Temp / Humidity / CO₂ / VOC|
+-------------+---------------+
              |
              v
      Embedded Linux Device
      (AI + IoT Application)
              |
   +----------+-----------+
   | Edge AI Inference    |
   | Camera Processing   |
   +----------+-----------+
              |
              v
        CoreIoT Platform
  (Dashboard, Alerts, Storage)
```

## 4. Key Features

- Industrial sensor integration via Modbus RS-485
- Edge AI inference for people counting and fatigue detection
- Camera-based monitoring using embedded AI models
- Real-time visualization and alerting via CoreIoT
- Modular and extensible software architecture
- Designed for Yocto-based embedded Linux systems

## 5. Repository Structure

```
src-lsmy/
├── docs/
│   ├── system-architecture.md
│   └── api-specification.md
│
├── sensor/
│   ├── modbus/
│   │   ├── modbus_reader.py
│   │   └── sensor_parser.py
│
├── ai/
│   ├── models/
│   │   ├── people_counting/
│   │   └── fatigue_detection/
│   ├── inference/
│   │   └── edge_inference.py
│
├── camera/
│   └── camera_manager.py
│
├── coreiot/
│   ├── mqtt_client.py
│   └── data_uploader.py
│
├── utils/
│   └── logger.py
│
├── config/
│   └── system.yaml
│
├── main.py
└── README.md
```

Structure may vary depending on implementation language (Python / C++).

## 6. Technologies Used

- **Embedded Linux (Yocto-based)**
- **Modbus RS-485**
- **CoreIoT Platform**
- **TensorFlow Lite / ONNX Runtime**
- **OpenCV / V4L2**
- **MQTT / REST APIs**

## 7. Installation & Deployment (Overview)

### 7.1 Build Environment

- Embedded Linux device (ARM-based)
- Camera supported by V4L2
- RS-485 interface enabled

### 7.2 Run Application

```bash
python3 main.py
```

Detailed deployment steps depend on the target hardware and Yocto image configuration.

## 8. Evaluation Metrics

The system is evaluated based on:

- AI inference accuracy
- End-to-end latency
- System stability
- Energy consumption
- Scalability and extensibility

## 9. Future Work

- Advanced AI models for safety compliance
- Multi-camera support
- Hardware acceleration (NPU / GPU)
- Secure OTA update integration
- Large-scale deployment support

## 10. License

This project is intended for **academic and research use**.
