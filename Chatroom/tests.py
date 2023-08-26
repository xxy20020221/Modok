# 你的代码包含两个 WebSocket 消费者：一个用于团队群聊 (`ChatConsumer`)，另一个用于直接私聊 (`DirectChatConsumer`)。每个消费者都期望接收一个 JSON 格式的消息，该消息包含消息类型和内容。
#
# 以下是一些你可以使用的 JSON 格式的测试消息：
#
# 1. **团队群聊 (`ChatConsumer`)**:
#
#    a. 文本消息:
#       ```json
#       {
#           "type": "text",
#           "content": "Hello, team!"
#       }
#       ```
#
#    b. 图片消息 (这里，`content` 是图片消息的 ID，你可能需要根据你的数据库中的实际数据进行更改)：
#       ```json
#       {
#           "type": "image",
#           "content": "123456"
#       }
#       ```
#
#    c. 文件消息 (同样，`content` 是文件消息的 ID)：
#       ```json
#       {
#           "type": "file",
#           "content": "789012"
#       }
#       ```
#
#    d. 文本消息，包含 @ 提及:
#       ```json
#       {
#           "type": "text",
#           "content": "Hey @all, check this out!"
#       }
#       ```
#
# 2. **直接私聊 (`DirectChatConsumer`)**:
#
#    a. 文本消息:
#       ```json
#       {
#           "type": "text",
#           "content": "Hey there, how are you?"
#       }
#       ```
#
#    b. 图片消息:
#       ```json
#       {
#           "type": "image",
#           "content": "234567"
#       }
#       ```
#
#    c. 文件消息:
#       ```json
#       {
#           "type": "file",
#           "content": "890123"
#       }
#       ```
#
# 要测试这些消息，你可以使用前面提到的方法（例如，使用浏览器的开发者工具或 WebSocket 客户端工具）将这些 JSON 消息发送到你的 WebSocket 服务器。
#
# 此外，当你在实际应用中实现客户端时，确保客户端在发送消息时使用上述格式，并根据你的数据库中的实际数据调整内容字段。