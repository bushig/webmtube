import os
from tempfile import NamedTemporaryFile

from hachoir.editor import createEditor
from hachoir.parser import createParser
from hachoir.stream import OutputStream
from hachoir.strip import BasicStripper

from webmtube.utils import get_file_md5


def TemporaryFileOutputStream():
    """
    Create an output stream into Temporary file.

    Filename have to be unicode, whereas (optional) real_filename can be str.
    """
    temp_file = NamedTemporaryFile(delete=False, suffix=".webm")
    # print(temp_file.name)
    return OutputStream(temp_file, filename=temp_file.name)


# Removes in WEBM everything except video/audio containers
class MkvStripper(BasicStripper):
    def stripSub(self, editor):
        total = 0  # how many bytes to remove
        for field in editor:
            if field.name.startswith("EBML") or field.name.startswith("Void"):
                # print(field.name, field.size)
                size = self.removeField(field, editor)
                total += size
            elif field.name.startswith('Segment'):
                # TODO: probably should update size value
                size = self.stripSub(field)
                total += size
        return total

    def strip(self):
        return self.stripSub(self.editor)


def stripEditor(editor):
    stripper = MkvStripper(editor, 0)

    if stripper():
        # output = FileOutputStream('test.webm')
        output = TemporaryFileOutputStream()
        with output:
            editor.writeInto(output)
        return output
    else:
        raise Exception("Stripper is not suitable")  # TODO: Refactor to except mp4


def strip_webm(filename):
    parser = createParser(filename)
    editor = createEditor(parser)

    output = stripEditor(editor)
    # print(output.filename)
    return output.filename


def hash_stripped_webm(filename):
    md5 = ""
    with open(filename, 'rb') as output_file:
        md5 = get_file_md5(output_file)
    os.remove(filename)
    return md5

# strip_webm("webm_files/3.webm")
