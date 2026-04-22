# Camera Lock Settings — Software-Only Capture Optimization

## The Problem

Smartphone ISPs (Image Signal Processors) automatically "correct" white balance,
exposure, and tone mapping. This destroys the subtle spectral information we need.

A warm-lit room makes the ISP add blue. A cool-lit room makes it add yellow.
The R-channel ratio we're measuring (Layla 590-670nm proxy) gets normalized
away by auto-WB before we ever see the pixel values.

## The Solution: Lock Everything

When the app enters capture mode, lock ALL auto-processing:

### iOS (AVFoundation)

```swift
let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back)!
try device.lockForConfiguration()

// 1. Lock White Balance — MOST CRITICAL
device.whiteBalanceMode = .locked
// Lock at current gains (user points at white paper first)

// 2. Lock Exposure
device.exposureMode = .locked
// Or use custom: device.setExposureModeCustom(duration: CMTime(1,100), iso: 100)

// 3. Lock Focus at ~15-20cm
device.focusMode = .locked
device.setFocusModeLockedWithLensPosition(0.55) // ~15-20cm

// 4. Flash OFF
device.torchMode = .off

device.unlockForConfiguration()

// 5. Capture format: HEIF max quality (or RAW if available)
let settings = AVCapturePhotoSettings(format: [AVVideoCodecKey: AVVideoCodecType.hevc])
settings.flashMode = .off
```

### Android (Camera2 API)

```kotlin
val captureBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE)

// 1. Lock White Balance — MOST CRITICAL
captureBuilder.set(CaptureRequest.CONTROL_AWB_MODE, CaptureRequest.CONTROL_AWB_OFF)
captureBuilder.set(CaptureRequest.COLOR_CORRECTION_MODE,
    CaptureRequest.COLOR_CORRECTION_MODE_TRANSFORM_MATRIX)
// Set neutral gains (1:1:1) — calibration module handles correction
captureBuilder.set(CaptureRequest.COLOR_CORRECTION_GAINS,
    RggbChannelVector(1.0f, 1.0f, 1.0f, 1.0f))

// 2. Lock Exposure
captureBuilder.set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_OFF)
captureBuilder.set(CaptureRequest.SENSOR_EXPOSURE_TIME, 10_000_000L) // 10ms
captureBuilder.set(CaptureRequest.SENSOR_SENSITIVITY, 100) // ISO 100

// 3. Lock Focus
captureBuilder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_OFF)
captureBuilder.set(CaptureRequest.LENS_FOCUS_DISTANCE, 5.0f) // ~20cm

// 4. Flash OFF
captureBuilder.set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_OFF)

// 5. Disable all post-processing
captureBuilder.set(CaptureRequest.NOISE_REDUCTION_MODE,
    CaptureRequest.NOISE_REDUCTION_MODE_OFF)
captureBuilder.set(CaptureRequest.EDGE_MODE, CaptureRequest.EDGE_MODE_OFF)
captureBuilder.set(CaptureRequest.COLOR_CORRECTION_ABERRATION_MODE,
    CaptureRequest.COLOR_CORRECTION_ABERRATION_MODE_OFF)
```

## White Balance Calibration Flow

Since we lock WB to neutral, we need software calibration.
The WHITE PAPER visible in every capture IS our calibration reference.

Flow:
1. User places cup on white paper (already in protocol)
2. App locks camera settings
3. App captures image
4. Software detects white paper region around the cup
5. Samples mean RGB of white paper → this is the "illuminant"
6. Normalizes: corrected_pixel = raw_pixel / white_paper_rgb * 255
7. Now R-channel values are illuminant-independent

This replaces the physical calibration card entirely.
The white paper IS the card. Every home has white paper.
