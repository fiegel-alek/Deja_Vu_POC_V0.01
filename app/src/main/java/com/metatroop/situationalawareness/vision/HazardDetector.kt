package com.metatroop.situationalawareness.vision

import com.metatroop.situationalawareness.alert.Detection

interface HazardDetector {
    suspend fun detect(frame: CameraFrame): List<Detection>
}
