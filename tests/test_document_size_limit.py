import unittest
from unittest.mock import MagicMock
import telebot
# Assuming we can import the handler directly for test
from handlers.message_handler import handle_document

class TestDocumentHandler(unittest.TestCase):
    def setUp(self):
        self.bot = MagicMock()
        # Need to set up the global bot if it's not already
        from handlers import message_handler
        message_handler.bot = self.bot
        
    def test_file_too_large_rejected(self):
        message = MagicMock()
        message.document.file_size = 20 * 1024 * 1024 # 20 MB > 19 MB
        message.document.file_name = "test.txt"
        
        handle_document(message)
        
        # Verify get_file was NOT called
        self.bot.get_file.assert_not_called()
        # Verify error message sent
        self.assertTrue(self.bot.reply_to.called or self.bot.send_message.called)
        
    def test_file_within_limit_processed(self):
        message = MagicMock()
        message.document.file_size = 10 * 1024 * 1024 # 10 MB < 19 MB
        message.document.file_id = "test_id"
        message.document.file_name = "test.txt"
        
        # Mock file info and download
        self.bot.get_file.return_value.file_path = "path/to/file"
        self.bot.download_file.return_value = b"some content"
        
        # Mock document_service to avoid real processing
        import services.document_service
        services.document_service.process_document = MagicMock(return_value=["some content"])
        
        handle_document(message)
        
        # Verify get_file was called
        self.bot.get_file.assert_called_with("test_id")

if __name__ == '__main__':
    unittest.main()
