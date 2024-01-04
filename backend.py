from lingua import Language, LanguageDetectorBuilder
from libretranslatepy import LibreTranslateAPI


class DetectorBackend:
    def __init__(self, lang_dict_detector):
        self._notes = []
        self._note2lang = {}
        for language, note in lang_dict_detector.items():
            try:
                note_detector = getattr(Language, note)
            except AttributeError as e:
                print(e)
                print(f"Failed recognizing note {note} in Detector.")
                raise AttributeError
            assert note_detector not in self._notes, f"Repeat detector note {note}!"
            self._notes.append(note_detector)
            self._note2lang[note_detector] = language

        self._detector = LanguageDetectorBuilder.from_languages(*self._notes).build()

    def detect(self, content: str) -> str:
        detected_note = self._detector.detect_language_of(content)
        return self._note2lang[detected_note] if detected_note else None
        

class TranslatorBackend:
    need_src_lang = True

    def __init__(self, lang_dict_translator):    
        self._lang2note = {}
        for language, note in lang_dict_translator.items():
            assert language not in self._lang2note.keys(), f"Repeat translator lang {language}!"
            self._lang2note[language] = note

        self._translator = LibreTranslateAPI("http://127.0.0.1:18888")

    def translate(self, content: str, src_lang: str, dst_lang: str) -> str:
        src_lang = self._lang2note[src_lang]
        dst_lang = self._lang2note[dst_lang]
        return self._translator.translate(content, src_lang, dst_lang)
