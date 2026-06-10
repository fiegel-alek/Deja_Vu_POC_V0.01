package com.metatroop.situationalawareness.monitoring

import com.metatroop.situationalawareness.alert.AlertEngine
import com.metatroop.situationalawareness.vision.CameraFrame
import com.metatroop.situationalawareness.vision.FrameSampler
import com.metatroop.situationalawareness.vision.HazardDetector

class FrameProcessor(
    private val frameSampler: FrameSampler,
    private val hazardDetector: HazardDetector,
    private val alertEngine: AlertEngine,
) {
    suspend fun process(frame: CameraFrame): FrameProcessingResult {
        if (!frameSampler.shouldProcess(frame)) {
            return FrameProcessingResult(processed = false)
        }

        val detections = hazardDetector.detect(frame)
        return FrameProcessingResult(
            processed = true,
            detectionsEvaluated = detections.size,
            alerts = alertEngine.evaluate(detections),
        )
    }
}
