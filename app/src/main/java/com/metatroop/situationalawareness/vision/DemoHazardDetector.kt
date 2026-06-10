package com.metatroop.situationalawareness.vision

import com.metatroop.situationalawareness.alert.Detection

class DemoHazardDetector : HazardDetector {
    override suspend fun detect(frame: CameraFrame): List<Detection> {
        val detections = mutableListOf<Detection>()

        if ("weapon_visible" in frame.demoSignals) {
            detections += Detection(
                label = "weapon_visible",
                confidence = 0.82,
                timestampMs = frame.timestampMs,
                direction = "ahead",
            )
        }

        if ((frame.luminance ?: 1.0) < LOW_LIGHT_LUMINANCE) {
            detections += Detection(
                label = "low_light",
                confidence = 0.72,
                timestampMs = frame.timestampMs,
            )
        }

        return detections
    }

    private companion object {
        const val LOW_LIGHT_LUMINANCE = 0.18
    }
}
