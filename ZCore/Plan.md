# DEFINITION


# Strength
1. Simple process (minimize learning curve)
    - Simple UI control
    - Interactive process (enable to see a bit of jnt structure)
2. Extendable modular process (object base)
    - Treat body part as object (node editor for more extensive rig)
3. Very easy to modify 
4. Lightweight rig (optimized)

# Back-End Concept:
Rig part class (mouth/eye/nose/etc) named as **Facial element/element** contain:
- Native procedure/ Natural object (How it arrange function and manage it) (input: selection (face,edge,etc), Position)
- extensive modular attribute with node editor

# all objects for face rig
- eyes
- eyelid (done)
- lips
- nose
- cheek
- eyebrow 
- **experiment** neck muscle (tense)
- **experiment** muscle simulation (need attach to attr for show and hide manual ctrl and trigger effect with auto (follow anatomical behavior) or manual intensity) (many small ctrl)

# Highlight features:
- import export module (previous build rig)
- build rig system as object/node
- interactive (spline/manual jnt)
- **experiment** muscle simulation
- **experiment** texture driven wrinkle
- **experiment** ikfk snap

# Element identity:
- **mouth** > lips seal, lipsync, protrude lips, nasolabial fold 
- **jaw** > chewing

# SOP:
- create object class setup 
- create object class build
- refactor to maya util/parent class
- design / override color / correct scale
- nodes creation (circuit, data, etc) / attribute + advance customization

#################################################################################################
# TESTING
- snarl expression
- stank face
- wide smile/genuine smile
- extreme smile with eyes close
- shock 
- horrified
- smirk face/haewonbear face