# Safety Boundaries

## Allowed Classification Target

The app should identify observable objects, hazards, and environmental conditions:

- Visible weapon-like object.
- Vehicle approaching.
- Fire or smoke.
- Obstacle.
- Person very close.
- Low light or obstructed camera.

The app can report probability, direction, and uncertainty.

## Disallowed Classification Target

The app should not classify people as hostile, suspicious, dangerous, criminal, or safe based on identity, appearance, clothing, face, gait, ethnicity, disability, neighborhood, or other personal characteristics.

The app should not perform face recognition, identity lookup, watchlist matching, or target selection.

## Wording Rules

Use observable wording:

- Good: "Possible weapon visible ahead, 82 percent."
- Good: "Person close on right, 74 percent."
- Avoid: "Hostile person ahead."
- Avoid: "Threat confirmed."

## Decision Rules

The app should assist awareness, not make decisions. Alerts must be framed as uncertain sensor observations and should never instruct the user to confront, pursue, aim at, or harm anyone.

## Logging Rules

For local debugging, store:

- Detection label.
- Confidence.
- Timestamp.
- Whether an alert was spoken.

Avoid storing raw images or video unless the user explicitly enables it and the app has a clear retention policy.
