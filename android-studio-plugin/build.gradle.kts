plugins {
    id("java")
    id("org.jetbrains.kotlin.jvm") version "2.1.0"
    id("org.jetbrains.intellij") version "1.17.3"
}

group = "com.pantikur"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // Корутинки есть в IDE
    compileOnly("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
}

// Используем локальную Android Studio
intellij {
    localPath = file("D:/pant/445").absolutePath
    plugins = listOf()
}

kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xskip-metadata-version-check")
    }
}

tasks {
    patchPluginXml {
        sinceBuild = "261"
        untilBuild = "261.*"
    }
    
    buildSearchableOptions {
        enabled = false
    }
}
