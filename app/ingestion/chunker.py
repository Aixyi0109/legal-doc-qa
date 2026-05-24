from langchain_text_splitters import RecursiveCharacterTextSplitter
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
    

class Chunker:
    def __init__(self, size: int, overlap: int):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)

    def chunk(self, pages: list[dict]) -> list[dict]:
        """输入 [{"page": 1, "text": "..."}],输出 [{"chunk_id": "...", "chunk_index": 1, "page": 1, "text": "..."}]"""
        chunks = []
        chunk_index = 0
        for page in pages:
            page_chunks = self.splitter.split_text(page["text"])
            for i, chunk in enumerate(page_chunks):
                chunk_index += 1
                chunks.append({"chunk_id": f"{page['page']}_{i + 1}", "chunk_index": chunk_index, "page": page["page"], "text": chunk})
        return chunks
    
