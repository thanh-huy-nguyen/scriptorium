"""Typographic fixes to a fetched reference are allowed; changes to what it says are not."""
import unittest

from scriptorium import cite

FETCHED = ("@article{frenay2014, title={Classification in the Presence of Label Noise: A Survey}, "
           "author={Frenay, Benoit and Verleysen, Michel}, year={2014}, pages={845–869} }")


class ContentHash(unittest.TestCase):
    def test_typographic_fixes_keep_the_fingerprint(self):
        fixed = ("@article{frenay2014,\n  title = {Classification in the Presence of Label Noise: {A} Survey},\n"
                 "  author = {Fr{\\'e}nay, Benoit and Verleysen, Michel},\n  year = {2014},\n  pages = {845--869},\n"
                 "  note = {Survey}\n}")
        self.assertEqual(cite.content_hash(FETCHED), cite.content_hash(fixed))

    def test_changes_of_content_break_it(self):
        for old, new in (("{2014}", "{2015}"), ("Label Noise", "Label Errors"), ("Verleysen", "Smith"),
                         ("845–869", "845–870")):
            self.assertNotEqual(cite.content_hash(FETCHED), cite.content_hash(FETCHED.replace(old, new)), new)

    def test_plain_decodes_accents_and_dashes(self):
        self.assertEqual(cite._plain("Fr{\\'e}nay"), "frenay")
        self.assertEqual(cite._plain("Sáez"), "saez")
        self.assertEqual(cite._plain("13723--13732"), cite._plain("13723–13732"))


if __name__ == "__main__":
    unittest.main()
