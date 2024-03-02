import regex as re

_PATTERNS = {
    'url': r'<[^: >]+:\/[^ >]+>|(?:https?|steam):\/\/[^\s<]+[^<.,:;\"\'\]\s]',
    'mention_all': r'@here|@everyone',
    'mention_spec': r'<@&?\d+>',
    'mention_ch': r'<#\d+>',
    'cus_emoji': r'<a?:\w+:\d+>',
    'emoji': r"[\U0001F600-\U0001F64F" 
    		   "\U0001F300-\U0001F5FF"
               "\U0001F680-\U0001F6FF"
               "\U0001F1E0-\U0001F1FF]+",
    'markdown': r'[_\\~|\*`#-]|^>(?:>>)?\s|\[.+\]\(.+\)',
}

_PATTERN_WITHOUT_LINE_BREAK = r"({})".format("|".join(_PATTERNS.values()))
_PATTERN_WITH_LINE_BREAK = r"({})".format("|".join([r'\n'] + list(_PATTERNS.values())))
_PATTERN_START_SPACES = r"(^\s+)"
_PATTERN_END_SPACES = r"(\s+$)"


class TranslationParser:
    def __init__(self, detector, translator):
        self._reg_pattern = re.compile(_PATTERN_WITHOUT_LINE_BREAK)
        self._reg_pattern_lb = re.compile(_PATTERN_WITH_LINE_BREAK)
        self._reg_pattern_start_ws = re.compile(_PATTERN_START_SPACES)
        self._reg_pattern_end_ws = re.compile(_PATTERN_END_SPACES)

        self._attachment_urls = []
        self._embeds = []

        self._return_original = True
        self._origin_lang = None
        self._origin_msg = None
        self._cutted_msg = []
        self._separators = []

        self._detector = detector
        self._translator = translator

    def load_input(self, message):
        # extract content
        self._attachment_urls = [attach.url for attach in message.attachments]
        self._embeds = message.embeds
        self._origin_msg = message.content
        if self._origin_msg.strip() == "":
            self._origin_msg = None
            return

        # detect source language
        detect_content = re.sub(self._reg_pattern, "", self._origin_msg)
        detect_content = re.sub(r'\n\s*\n', '\n\n', detect_content)
        if detect_content.strip() == "":
            return
        
        if self._detector is None:
            self._return_original = False
            return

        self._origin_lang = self._detector.detect(detect_content)
        if self._origin_lang is None:
            return

        # split content
        self._separators = re.findall(self._reg_pattern_lb, self._origin_msg)
        self._cutted_msg = re.split(self._reg_pattern_lb, self._origin_msg)
        self._return_original = False

    def translate_message(self, target_lang):
        if self._return_original:
            return self._origin_msg, self._embeds, self._attachment_urls
        separator_idx = 0
        result_cutted_msg = []
        for msg_seg in self._cutted_msg:
            if msg_seg == "":
                continue
            if separator_idx < len(self._separators) and msg_seg == self._separators[separator_idx]:
                separator_idx += 1
                result_cutted_msg.append(msg_seg)
            elif msg_seg.strip() != "":
                translated_seg = self._translator.translate(msg_seg, self._origin_lang, target_lang)
                start_ws = re.findall(self._reg_pattern_start_ws, msg_seg)
                end_ws = re.findall(self._reg_pattern_end_ws, msg_seg)
                if start_ws:
                    result_cutted_msg.append(start_ws[0])
                result_cutted_msg.append(translated_seg)
                if end_ws:
                    result_cutted_msg.append(end_ws[0])
            else:
                result_cutted_msg.append(msg_seg)
        result_msg = "".join(result_cutted_msg)
        return result_msg, self._embeds, self._attachment_urls
