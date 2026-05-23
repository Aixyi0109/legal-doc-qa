class FixedLengthChunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        chunks = []
        start = 0
        step = self.chunk_size - self.overlap

        while start < len(text):
            chunks.append(text[start:start + self.chunk_size])
            start += step

        return chunks

    def chunk_by_hanzi(self, text: str) -> list[str]:
        chunks = []
        current_chunk = []
        han_count = 0

        for char in text:
            current_chunk.append(char)
            if '\u4e00' <= char <= '\u9fff':
                han_count += 1
            if han_count >= self.chunk_size:
                chunks.append("".join(current_chunk))
                current_chunk = []
                han_count = 0

        if current_chunk:  # 最后一段
            chunks.append("".join(current_chunk))

        return chunks

