"""Tests for FilesystemCore business logic."""

import tempfile
from pathlib import Path

import pytest

from filesystem_mcp.core import FileSizeError, FilesystemCore, FilesystemError, SecurityError
from filesystem_mcp.models import (
    FilesystemConfig,
    GlobRequest,
    ListDirRequest,
    PatchFileRequest,
    ReadFileRequest,
    SearchFilesRequest,
    WriteFileRequest,
)


class TestFilesystemCore:
    """Tests for FilesystemCore."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config(self, temp_dir):
        """Create a test configuration."""
        return FilesystemConfig(
            root_path=temp_dir,
            max_file_size=1024 * 1024,  # 1 MB for tests
            follow_symlinks=False,
            allow_absolute_paths=False,
            default_encoding="utf-8",
        )

    @pytest.fixture
    def core(self, config):
        """Create a FilesystemCore instance."""
        return FilesystemCore(config)

    def test_resolve_path_relative(self, core, temp_dir):
        """Test resolving relative paths."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("hello")
        resolved = core._resolve_path("test.txt")
        assert resolved == test_file.resolve()

    def test_resolve_path_outside_root_raises(self, core, temp_dir):
        """Test that paths outside root raise SecurityError."""
        with pytest.raises(SecurityError):
            core._resolve_path("../outside.txt")

    def test_reserved_path_symlink_protection(self, core, temp_dir):
        """Test symlink protection when follow_symlinks=False."""
        import sys

        if sys.platform == "win32":
            pytest.skip("Symlink creation requires admin on Windows")

        # Create a real file
        real_file = temp_dir / "real.txt"
        real_file.write_text("real")

        # Create a symlink inside root pointing outside
        outside_dir = temp_dir.parent / "outside"
        outside_dir.mkdir(exist_ok=True)
        outside_file = outside_dir / "secret.txt"
        outside_file.write_text("secret")

        symlink = temp_dir / "link.txt"
        symlink.symlink_to(outside_file)

        with pytest.raises(SecurityError):
            core._resolve_path("link.txt")

    def test_read_file_success(self, core, temp_dir):
        """Test reading a file successfully."""
        test_file = temp_dir / "read_test.txt"
        test_file.write_text("Hello, World!")

        request = ReadFileRequest(path="read_test.txt")
        response = core.read_file(request)

        assert response.path == "read_test.txt"
        assert response.content == "Hello, World!"
        assert response.size == 13
        assert response.encoding == "utf-8"
        assert response.is_binary is False

    def test_read_file_not_found(self, core):
        """Test reading a non-existent file raises error."""
        with pytest.raises(FilesystemError) as exc:
            core.read_file(ReadFileRequest(path="nonexistent.txt"))
        assert exc.value.code == "NOT_FOUND"

    def test_read_file_not_a_file(self, core, temp_dir):
        """Test reading a directory raises error."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        with pytest.raises(FilesystemError) as exc:
            core.read_file(ReadFileRequest(path="subdir"))
        assert exc.value.code == "NOT_A_FILE"

    def test_read_file_size_limit(self, core, temp_dir):
        """Test file size limit on read."""
        large_file = temp_dir / "large.txt"
        large_file.write_text("x" * 2000)  # 2 KB

        with pytest.raises(FileSizeError):
            core.read_file(ReadFileRequest(path="large.txt", max_size=1000))

    def test_read_binary_file(self, core, temp_dir):
        """Test reading a binary file returns base64."""
        binary_file = temp_dir / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe\xfd")

        request = ReadFileRequest(path="binary.bin")
        response = core.read_file(request)

        assert response.is_binary is True
        import base64

        decoded = base64.b64decode(response.content)
        assert decoded == b"\x00\x01\x02\x03\xff\xfe\xfd"

    def test_write_file_success(self, core, temp_dir):
        """Test writing a file successfully."""
        request = WriteFileRequest(path="new_file.txt", content="Hello, World!")
        response = core.write_file(request)

        assert response.path == "new_file.txt"
        assert response.size == 13
        assert response.encoding == "utf-8"

        # Verify file was written
        written = (temp_dir / "new_file.txt").read_text()
        assert written == "Hello, World!"

    def test_write_file_creates_dirs(self, core, temp_dir):
        """Test write_file creates parent directories."""
        request = WriteFileRequest(
            path="nested/deep/file.txt",
            content="deep",
            create_dirs=True,
        )
        response = core.write_file(request)

        assert response.path == "nested/deep/file.txt"
        assert (temp_dir / "nested" / "deep" / "file.txt").read_text() == "deep"

    def test_write_file_atomic(self, core, temp_dir):
        """Test atomic write prevents partial writes."""
        file_path = temp_dir / "atomic.txt"
        file_path.write_text("original")

        # This should work
        request = WriteFileRequest(path="atomic.txt", content="new content", atomic=True)
        core.write_file(request)

        assert file_path.read_text() == "new content"

    def test_write_file_size_limit(self, core, temp_dir):
        """Test write file size limit."""
        large_content = "x" * (2 * 1024 * 1024)  # 2 MB

        with pytest.raises(FileSizeError):
            core.write_file(WriteFileRequest(path="large.txt", content=large_content))

    def test_list_dir_success(self, core, temp_dir):
        """Test listing directory contents."""
        (temp_dir / "file1.txt").write_text("a")
        (temp_dir / "file2.py").write_text("b")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file3.txt").write_text("c")

        request = ListDirRequest(path=".")
        response = core.list_dir(request)

        assert response.path == "."
        assert response.total == 3
        names = [e.name for e in response.entries]
        assert "file1.txt" in names
        assert "file2.py" in names
        assert "subdir" in names

    def test_list_dir_with_glob(self, core, temp_dir):
        """Test list_dir with glob pattern."""
        (temp_dir / "test.py").write_text("a")
        (temp_dir / "test.txt").write_text("b")
        (temp_dir / "other.py").write_text("c")

        request = ListDirRequest(path=".", glob_pattern="test*")
        response = core.list_dir(request)

        assert response.total == 2
        names = [e.name for e in response.entries]
        assert "test.py" in names
        assert "test.txt" in names
        assert "other.py" not in names

    def test_list_dir_recursive(self, core, temp_dir):
        """Test recursive directory listing."""
        (temp_dir / "file1.txt").write_text("a")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "file2.txt").write_text("b")
        (temp_dir / "subdir" / "deep").mkdir()
        (temp_dir / "subdir" / "deep" / "file3.txt").write_text("c")

        request = ListDirRequest(path=".", recursive=True)
        response = core.list_dir(request)

        assert response.total == 5  # file1, subdir, file2, deep, file3

    def test_list_dir_not_found(self, core):
        """Test listing non-existent directory."""
        with pytest.raises(FilesystemError) as exc:
            core.list_dir(ListDirRequest(path="nonexistent"))
        assert exc.value.code == "NOT_FOUND"

    def test_search_files_success(self, core, temp_dir):
        """Test searching files with ripgrep."""
        (temp_dir / "test.py").write_text("def hello():\n    print('hello')\n")
        (temp_dir / "test.js").write_text("function hello() {\n    console.log('hello');\n}")

        request = SearchFilesRequest(pattern="hello", path=".")
        response = core.search_files(request)

        assert response.pattern == "hello"
        assert response.path == "."
        assert response.total >= 2  # At least 2 matches

    def test_search_files_not_found(self, core):
        """Test searching in non-existent directory."""
        with pytest.raises(FilesystemError) as exc:
            core.search_files(SearchFilesRequest(pattern="test", path="nonexistent"))
        assert exc.value.code == "NOT_FOUND"

    def test_glob_success(self, core, temp_dir):
        """Test glob pattern matching."""
        (temp_dir / "test.py").write_text("a")
        (temp_dir / "test.txt").write_text("b")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "test.py").write_text("c")

        request = GlobRequest(pattern="**/*.py", path=".")
        response = core.glob(request)

        assert response.pattern == "**/*.py"
        assert response.total == 2
        matches = set(response.matches)
        assert "test.py" in matches
        # Handle both forward and backslash separators (Windows compatibility)
        assert any(m.replace("\\", "/") == "subdir/test.py" for m in matches)

    def test_glob_not_found(self, core):
        """Test glob in non-existent directory."""
        with pytest.raises(FilesystemError) as exc:
            core.glob(GlobRequest(pattern="*.py", path="nonexistent"))
        assert exc.value.code == "NOT_FOUND"

    def test_patch_file_success(self, core, temp_dir):
        """Test patching a file."""
        test_file = temp_dir / "patch_test.txt"
        test_file.write_text("Hello world\nHello again")

        request = PatchFileRequest(path="patch_test.txt", old_str="Hello", new_str="Hi")
        response = core.patch_file(request)

        assert response.path == "patch_test.txt"
        assert response.replacements == 2
        assert response.new_size == len("Hi world\nHi again")

        content = test_file.read_text()
        assert content == "Hi world\nHi again"

    def test_patch_file_old_str_not_found(self, core, temp_dir):
        """Test patch with old_str not in file."""
        test_file = temp_dir / "patch_test.txt"
        test_file.write_text("Hello world")

        with pytest.raises(FilesystemError) as exc:
            core.patch_file(
                PatchFileRequest(path="patch_test.txt", old_str="Goodbye", new_str="Hi")
            )
        assert exc.value.code == "PATCH_FAILED"

    def test_patch_file_size_limit(self, core, temp_dir):
        """Test patch file size limit."""
        test_file = temp_dir / "patch_test.txt"
        test_file.write_text("a" * 500_000)  # 500 KB

        # Patch to make it larger than 1 MB limit
        with pytest.raises(FileSizeError):
            core.patch_file(
                PatchFileRequest(
                    path="patch_test.txt",
                    old_str="a" * 100,
                    new_str="b" * 600_000,  # Would make file ~1.1 MB
                )
            )

    # Additional tests for coverage

    def test_resolve_path_absolute_allowed(self, temp_dir):
        """Test resolving absolute paths when allowed."""
        config = FilesystemConfig(
            root_path=temp_dir,
            max_file_size=1024 * 1024,
            follow_symlinks=False,
            allow_absolute_paths=True,
            default_encoding="utf-8",
        )
        core = FilesystemCore(config)
        test_file = temp_dir / "absolute_test.txt"
        test_file.write_text("absolute")

        resolved = core._resolve_path(str(test_file))
        assert resolved == test_file.resolve()

    def test_resolve_path_absolute_not_allowed(self, core, temp_dir):
        """Test resolving absolute paths raises when not allowed."""
        test_file = temp_dir / "absolute_test.txt"
        test_file.write_text("absolute")

        with pytest.raises(SecurityError):
            core._resolve_path(str(test_file))

    def test_symlink_protection_inside_root(self, core, temp_dir):
        """Test symlink protection for symlinks inside root."""
        import sys

        if sys.platform == "win32":
            pytest.skip("Symlink creation requires admin on Windows")

        # Create a real file
        real_file = temp_dir / "real.txt"
        real_file.write_text("real")

        # Create a symlink inside root pointing to another file in root
        symlink = temp_dir / "link.txt"
        symlink.symlink_to(real_file)

        with pytest.raises(SecurityError):
            core._resolve_path("link.txt")

    def test_read_file_non_atomic_write(self, core, temp_dir):
        """Test write_file with atomic=False."""
        request = WriteFileRequest(path="non_atomic.txt", content="non-atomic", atomic=False)
        response = core.write_file(request)

        assert response.path == "non_atomic.txt"
        assert (temp_dir / "non_atomic.txt").read_text() == "non-atomic"

    def test_write_file_without_create_dirs(self, core, temp_dir):
        """Test write_file without creating parent dirs fails."""
        with pytest.raises(FilesystemError) as exc:
            core.write_file(
                WriteFileRequest(
                    path="nested/deep/file.txt",
                    content="deep",
                    create_dirs=False,
                )
            )
        assert exc.value.code == "NOT_FOUND"

    def test_list_dir_not_a_directory(self, core, temp_dir):
        """Test list_dir on a file raises error."""
        test_file = temp_dir / "file.txt"
        test_file.write_text("content")

        with pytest.raises(FilesystemError) as exc:
            core.list_dir(ListDirRequest(path="file.txt"))
        assert exc.value.code == "NOT_A_DIR"

    def test_glob_non_existent(self, core):
        """Test glob on non-existent directory."""
        with pytest.raises(FilesystemError) as exc:
            core.glob(GlobRequest(pattern="*.py", path="nonexistent"))
        assert exc.value.code == "NOT_FOUND"

    def test_patch_file_not_a_file(self, core, temp_dir):
        """Test patch_file on a directory raises error."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        with pytest.raises(FilesystemError) as exc:
            core.patch_file(PatchFileRequest(path="subdir", old_str="a", new_str="b"))
        assert exc.value.code == "NOT_A_FILE"

    def test_patch_file_empty_old_str(self, core, temp_dir):
        """Test patch_file with empty old_str."""
        test_file = temp_dir / "patch_test.txt"
        test_file.write_text("hello")

        with pytest.raises(FilesystemError) as exc:
            core.patch_file(PatchFileRequest(path="patch_test.txt", old_str="", new_str="x"))
        assert exc.value.code == "PATCH_FAILED"
