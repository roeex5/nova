"""Lightweight wake word detection using continuous speech recognition"""

import threading
import time
import speech_recognition as sr


class LightweightWakeWordListener:
    """
    Lightweight wake word detection using Google Speech Recognition

    Pros: Fast, no heavy dependencies, easy to use
    Cons: Requires internet, less accurate than dedicated wake word models
    """

    def __init__(self, wake_phrase="hey browser", callback=None, device_index=None):
        """
        Initialize lightweight wake word listener

        Args:
            wake_phrase: Phrase to detect (default: "hey browser")
            callback: Function to call when wake phrase is detected
            device_index: Microphone device index (None for default)
        """
        self.wake_phrase = wake_phrase.lower()
        self.callback = callback
        self.device_index = device_index
        self.is_listening = False
        self.listener_thread = None
        self.stop_event = threading.Event()
        self.recognizer = sr.Recognizer()

    def start(self):
        """Start listening for wake phrase in background thread"""
        if self.is_listening:
            print("Wake phrase listener already running")
            return

        self.is_listening = True
        self.stop_event.clear()
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
        print(f"🎤 Listening for '{self.wake_phrase}'...")

    def stop(self):
        """Stop listening for wake phrase"""
        if not self.is_listening:
            return

        self.is_listening = False
        self.stop_event.set()

        if self.listener_thread:
            self.listener_thread.join(timeout=2)

        print("Wake phrase listener stopped")

    def _listen_loop(self):
        """Main listening loop (runs in background thread)"""
        try:
            # IMPORTANT:
            # We must not invoke the wake-word callback while holding an active
            # sr.Microphone context, because downstream code (e.g. SpeechToText)
            # may open its own sr.Microphone context to capture a command.
            # Nested/overlapping microphone contexts can cause device/resource conflicts.

            speech_detected_count = 0
            while not self.stop_event.is_set():
                wake_detected = False
                detected_text = None

                # Acquire microphone for wake-word listening
                with sr.Microphone(device_index=self.device_index) as source:
                    # Show which device was actually opened
                    actual_device = source.device_index
                    print(f"📍 Microphone opened: device_index={actual_device}")

                    # Get device info for diagnostic purposes
                    try:
                        import pyaudio
                        p = pyaudio.PyAudio()
                        device_info = p.get_device_info_by_index(
                            actual_device
                            if actual_device is not None
                            else p.get_default_input_device_info()['index']
                        )
                        print(f"   Device name: {device_info['name']}")
                        print(f"   Sample rate: {device_info['defaultSampleRate']}")
                        print(f"   Channels: {device_info['maxInputChannels']}")
                        p.terminate()
                    except Exception as e:
                        print(f"   (Could not get device details: {e})")

                    # Adjust for ambient noise once per (re)open
                    print("Calibrating for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    print(f"Ready! Energy threshold: {self.recognizer.energy_threshold}")

                    while not self.stop_event.is_set():
                        try:
                            # Listen for short phrases (non-blocking with timeout)
                            audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                            speech_detected_count += 1

                            # Recognize speech
                            try:
                                text = self.recognizer.recognize_google(audio).lower()
                                print(f"[DEBUG] Heard: '{text}' (checking for '{self.wake_phrase}')")

                                # Check if wake phrase is in the recognized text
                                if self.wake_phrase in text:
                                    wake_detected = True
                                    detected_text = text
                                    print(f"✓ Wake phrase detected in: '{text}'")
                                    break

                            except sr.UnknownValueError:
                                # Speech not understood - continue listening
                                print(
                                    f"[DEBUG] Speech detected but not understood "
                                    f"(attempt #{speech_detected_count})"
                                )
                            except sr.RequestError as e:
                                print(f"Speech recognition error: {e}")
                                self.stop_event.wait(5)  # Wait before retrying

                        except sr.WaitTimeoutError:
                            # No speech detected - continue listening
                            pass
                        except Exception as e:
                            if not self.stop_event.is_set():
                                print(f"Error in listener: {e}")
                            break

                # Microphone context has been released here.
                if self.stop_event.is_set():
                    break

                if wake_detected and self.callback:
                    # Give the OS/audio backend a tiny moment to fully release resources
                    time.sleep(0.1)
                    try:
                        self.callback()
                    except Exception as e:
                        # Don't kill the listener thread if callback fails
                        if not self.stop_event.is_set():
                            print(f"Error in wake word callback: {e}")
                    finally:
                        # Continue listening for the next wake phrase
                        pass

        except Exception as e:
            print(f"Failed to open microphone: {e}")
            import traceback
            traceback.print_exc()

    def is_running(self):
        """Check if listener is currently running"""
        return self.is_listening


# Speech-to-Text service 
class SpeechToText:
    """Speech-to-text service with multiple backend support"""

    def __init__(self, service='google', api_key=None, device_index=None):
        """
        Initialize speech-to-text service

        Args:
            service: 'google' (current) or 'whisper' (future)
            api_key: API key for service (if required)
            device_index: Microphone device index (None for default)
        """
        self.service = service
        self.api_key = api_key
        self.device_index = device_index

    def recognize(self, timeout=5, phrase_time_limit=None):
        """
        Listen and convert speech to text

        Args:
            timeout: Maximum time to wait for phrase to start (seconds)
            phrase_time_limit: Maximum time for phrase (seconds)

        Returns:
            str: Recognized text, or None if recognition failed
        """
        if self.service == 'google':
            return self._recognize_google(timeout, phrase_time_limit)
        elif self.service == 'whisper':
            return self._recognize_whisper(timeout, phrase_time_limit)
        else:
            raise ValueError(f"Unknown service: {self.service}")

    def _recognize_google(self, timeout, phrase_time_limit):
        """Use Google Speech Recognition"""
        import speech_recognition as sr

        recognizer = sr.Recognizer()

        with sr.Microphone(device_index=self.device_index) as source:
            # Show which device is being used
            actual_device = source.device_index
            print(f"🎤 Listening for command on device_index={actual_device}...")

            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

                print("Processing speech...")

                # Use Google Speech Recognition
                text = recognizer.recognize_google(audio)
                return text

            except sr.WaitTimeoutError:
                print("No speech detected")
                return None
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                return None

    def _recognize_whisper(self, timeout, phrase_time_limit):
        """
        Use OpenAI Whisper API (future implementation)

        TODO: Implement Whisper API integration
        """
        raise NotImplementedError(
            "OpenAI Whisper API not yet implemented. "
            "Use 'google' service for now."
        )
