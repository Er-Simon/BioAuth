# BioAuth
BioAuth is a multibiometric authentication system that combines face recognition and voice-based verification to
enhance the security and accuracy of authentication.

The authentication process is conducted in two distinct steps:

  • First Step - Multiple-Template Identification Open Set: Initially, an open-
  set multiple-template identification operation is performed using the user’s face.
  This involves comparing the captured facial features with a database of multiple
  templates to identify the user. The open-set nature means that the user may not
  be registered in the system and therefore not be present in the database.
  
  • Second Step - Voice-Based Verification: Based on the identification result
  from the first step, a second operation is carried out for voice-based verification.
  This step involves analyzing the user’s voice to confirm their identity. Voice
  verification acts as a secondary layer of authentication, adding an extra level of
