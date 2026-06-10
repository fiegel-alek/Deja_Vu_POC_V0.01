import java.util.Properties
import kotlin.io.path.exists
import kotlin.io.path.inputStream

pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)

    val localProperties =
        Properties().apply {
            val localPropertiesPath = rootDir.toPath().resolve("local.properties")
            if (localPropertiesPath.exists()) {
                load(localPropertiesPath.inputStream())
            }
        }

    repositories {
        google()
        mavenCentral()
        maven {
            url = uri("https://maven.pkg.github.com/facebook/meta-wearables-dat-android")
            credentials {
                username = ""
                password =
                    System.getenv("GITHUB_TOKEN")
                        ?: localProperties.getProperty("github_token")
                        ?: ""
            }
        }
    }
}

rootProject.name = "MetaTroopSituationalAwareness"
include(":app")
