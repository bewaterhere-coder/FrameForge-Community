# Sample Game Architecture

## Ownership

This document is the canonical architecture reference for this sample project. The project may change these rules without changing FrameForge Core.

## Runtime shape

- The main scene owns the game loop and the small sample state.
- The `Game` Node2D script owns player movement, collectible state and drawing.
- No autoload singleton is needed for this sample.
- No network, persistence, plugin or service layer is introduced.

## Boundaries

- Keep the sample small: one main scene and one gameplay script.
- Keep input, state updates and drawing inside the sample gameplay script until a real second use case requires a split.
- Do not add a generic framework or abstraction for a single caller.
- Keep engine-specific code inside the Godot project.

## Change policy

If the project grows, update this document when scene ownership, state ownership or module boundaries change. FrameForge findings are advisory and do not replace code review or Godot validation.
