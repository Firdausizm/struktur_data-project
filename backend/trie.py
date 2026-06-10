"""
Implementasi struktur data Trie untuk autocomplete pencarian buku.
Dibuat 100% tanpa library tambahan — hanya menggunakan tipe bawaan Python.
"""


class TrieNode:
    """Node dalam struktur data Trie."""

    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}  # Karakter → anak node
        self.is_end: bool = False                   # Menandai akhir sebuah kata/frasa
        self.frequency: int = 0                     # Berapa kali kata ini di-insert


class Trie:
    """
    Struktur data Trie untuk menyimpan dan mencari kata/frasa.

    Fitur:
    - Case-insensitive (semua dikonversi ke lowercase)
    - Menyimpan frequency agar saran bisa diurutkan berdasarkan popularitas
    - Metode get_suggestions() mengembalikan top-N saran
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """
        Masukkan kata/frasa ke dalam Trie.
        Jika kata sudah ada, frequency-nya bertambah.
        """
        word = word.lower().strip()
        if not word:
            return

        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end = True
        node.frequency += 1

    def search(self, word: str) -> bool:
        """Cek apakah kata/frasa ada secara utuh di dalam Trie."""
        word = word.lower().strip()
        node = self._find_node(word)
        return node is not None and node.is_end

    def _find_node(self, prefix: str) -> TrieNode | None:
        """Cari node yang sesuai dengan prefix. Return None jika tidak ditemukan."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def _collect_words(
        self,
        node: TrieNode,
        prefix: str,
        results: list[tuple[str, int]],
    ) -> None:
        """Kumpulkan semua kata yang ada di bawah node ini secara rekursif (DFS)."""
        if node.is_end:
            results.append((prefix, node.frequency))

        for char in sorted(node.children.keys()):
            self._collect_words(node.children[char], prefix + char, results)

    def starts_with(self, prefix: str) -> list[str]:
        """Kembalikan semua kata yang dimulai dengan prefix."""
        prefix = prefix.lower().strip()
        if not prefix:
            return []

        node = self._find_node(prefix)
        if node is None:
            return []

        results: list[tuple[str, int]] = []
        self._collect_words(node, prefix, results)
        return [word for word, _freq in results]

    def get_suggestions(self, prefix: str, limit: int = 10) -> list[str]:
        """
        Kembalikan top-N saran berdasarkan frequency (paling sering dicari duluan).
        Jika frequency sama, diurutkan secara alfabet.
        """
        prefix = prefix.lower().strip()
        if not prefix:
            return []

        node = self._find_node(prefix)
        if node is None:
            return []

        results: list[tuple[str, int]] = []
        self._collect_words(node, prefix, results)

        # Urutkan: frequency tertinggi dulu, lalu alfabet
        results.sort(key=lambda x: (-x[1], x[0]))

        return [word for word, _freq in results[:limit]]
