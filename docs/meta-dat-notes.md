# Meta Wearables DAT Notes

Current public development appears to be based on the Meta Wearables Device Access Toolkit, with third-party applications running on the paired mobile device rather than directly on the glasses OS.

Useful starting points:

- Android SDK repository: https://github.com/facebook/meta-wearables-dat-android
- Wearables Developer Center docs: https://wearables.developer.meta.com/
- Session lifecycle docs: https://wearables.developer.meta.com/docs/lifecycle-events
- Mock Device Kit docs: https://wearables.developer.meta.com/docs/mock-device-kit/

## Practical Implications

- Build the app as an Android or iOS mobile app.
- Treat the glasses as camera, microphone, speaker, and device sensors exposed through DAT.
- Use the Mock Device Kit early so development can continue without hardware attached.
- Expect session state to change asynchronously. The app must handle running, paused, and stopped states.
- Do not design the first version around installing an app directly onto the glasses.

## Android Dependency Shape

The DAT Android repository documents Gradle artifacts for:

- `mwdat-core`
- `mwdat-camera`
- `mwdat-mockdevice`

The SDK is distributed through GitHub Packages, so a real Android project will need a GitHub token with package read access during dependency resolution.
