import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
}

val localProperties =
    Properties().apply {
        val localPropertiesFile = rootProject.file("local.properties")
        if (localPropertiesFile.exists()) {
            localPropertiesFile.inputStream().use(::load)
        }
    }

android {
    namespace = "com.metatroop.situationalawareness"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.metatroop.situationalawareness"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.1.0"
        manifestPlaceholders["META_DAT_APPLICATION_ID"] =
            localProperties.getProperty("META_DAT_APPLICATION_ID", "replace_with_meta_dat_app_id")
        manifestPlaceholders["META_DAT_CLIENT_TOKEN"] =
            localProperties.getProperty("META_DAT_CLIENT_TOKEN", "replace_with_meta_dat_client_token")
    }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.15"
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.kotlinx.coroutines.android)

    implementation(libs.mwdat.core)
    implementation(libs.mwdat.camera)
    implementation(libs.mwdat.display)
    implementation(libs.mwdat.mockdevice)
    implementation(libs.mediapipe.tasks.vision)
}
