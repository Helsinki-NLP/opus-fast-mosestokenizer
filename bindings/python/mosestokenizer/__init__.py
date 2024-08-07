import os
import sys
from ctypes import cdll
from typing import List, Optional

__all__ = ['MosesTokenizer']

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_TOKENIZER_LIB_DIR = os.path.join(_THIS_DIR, 'lib')

# Set default TOKENIZER_SHARED_DIR if not set
os.environ['TOKENIZER_SHARED_DIR'] = os.environ.get(
    'TOKENIZER_SHARED_DIR',
    os.path.join(_THIS_DIR, 'share')
)

if os.path.isfile(os.path.join(_TOKENIZER_LIB_DIR, 'libmosestokenizer-dev.so')):
    # hack to find the required shared lib in _mosestokenizer import
    # without adding the directory to LD_LIBARARY_PATH
    cdll.LoadLibrary(os.path.join(_TOKENIZER_LIB_DIR, 'libmosestokenizer-dev.so'))

try:
    from mosestokenizer.lib import _mosestokenizer
except ImportError as e:
    _msg = "Failed to import mosestokenizer c++ library\n" + \
        "Full error log: {}".format(e.__repr__())
    raise RuntimeError(_msg)


class MosesTokenizer(_mosestokenizer.MosesTokenizer):
    """Moses tokenizer with C++ backend.

    Do note that there are differences in outputs between
    this implementation and the original.

    Example usage

    .. code-block:: py

        tokenizer = MosesTokenizer('en')
        tokens = tokenizer.tokenize(sent)
        reconstructed_sent = tokenizer.detokenize(tokens)

    """

    def __init__(
        self,
        lang: str = 'en',
        aggressive_dash_splits: bool = False,
        escape_xml: bool = False,
        unescape_xml: bool = False,
        preserve_xml_entities: bool = False,
        other_letters_p: bool = False,
        refined_punct_splits: bool = False,
        url_handling: bool = True,
        supersub: bool = False,
        penn: bool = False,
        verbose: bool = False,
        user_dir: Optional[str] = None,
    ):
        """
        Args:
            lang (str, optional): Language identifier. Defaults to 'en'.
            aggressive_dash_splits (bool, optional):
                Aggressively split hyphens. Defaults to False.
            escape_xml (bool, optional):
                Escape XML characters. Defaults to False.
            unescape_xml (bool, optional):
                Unescape XML characters. Defaults to False.
            preserve_xml_entities (bool, optional):
                Preserve HTML entities. Defaults to False.
            refined_punct_splits (bool, optional):
                Refined punctuation splitting. Defaults to False.
            url_handling (bool, optional): Handle URLs. Defaults to True.
            supersub (bool, optional): Account for numerical super and
                subscript conjoining. Defaults to False.
            penn (bool, optional): Use PENN tokenizer. Defaults to False.
            verbose (bool, optional): Print messages. Defaults to False.
            verbose (Optional[str], optional): User provided nonbreaking
                prefixes and protected patterns. Defaults to None.
        """
        params = _mosestokenizer.MosesTokenizerParameters()

        # TODO: Validate and expose other parameters
        # The reason for not exposing all params is because some of them are
        # not being used or necessary in the first place.
        params.lang_iso = lang

        params.aggro_p = aggressive_dash_splits
        params.escape_p = escape_xml
        params.unescape_p = unescape_xml
        params.entities_p = preserve_xml_entities
        params.other_letters_p = other_letters_p
        params.refined_p = refined_punct_splits
        params.url_p = url_handling
        params.supersub_p = supersub  # Numeric super and subscript conjoining
        params.penn_p = penn
        params.verbose_p = verbose

        # Unexposed arguments
        # Still under internal debate for expose or not
        params.detag_p  # Skip tag lines
        params.alltag_p  # Skip all tags
        params.split_breaks_p  # Splitter splits on linebreak

        # Unused parameters
        # Probably due unimplemented features
        params.normalize_p
        params.denumber_p
        params.narrow_latin_p
        params.narrow_kana_p

        # These variables should be kept for CLI only since they would
        # only add needless complexity to the feature set of the tokenizer
        params.drop_bad_p  # Drop control and unassigned unicode chars
        params.downcase_p  # Lowercase
        params.split_p  # Seems to be a dummy variable
        params.notokenization_p  # Dont perform tokenization
        params.para_marks_p  # Mark splits with <P>

        params.nthreads = 1
        params.chunksize = 1

        super().__init__(params)

        # Load custom protected patterns and prefixes
        self.init(os.environ['TOKENIZER_SHARED_DIR'])
        if user_dir is not None:
            self.init(user_dir)

    def tokenize(self, text: str) -> List[str]:
        """Tokenize a raw input text based on linguistic rules.

        Args:
            text (str): Raw input text.

        Returns:
            List[str]: List of tokens.
        """
        return super().tokenize(text)

    def detokenize(self, tokens: List[str]) -> str:
        """Combine a list of tokens back into a sentence.

        Args:
            tokens (List[str]): List of tokens generated by `tokenize`.

        Returns:
            str: Reconstructed sentence.
        """
        return super().detokenize(tokens)

    def split(self, text: str) -> List[str]:
        """Splits a text into multiple sentences based on linguistic rules.

        Args:
            text (str): Raw input text.
                Expecting a paragraph with a variable number of sentences.

        Returns:
            List[str]: List of sentences.
        """
        return super().split(text, False)
