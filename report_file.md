注：本文档内（...）用于解释数据格式和数据类型,....表省略

### ./report/

**该目录存储训练记录（json文件），其格式如下**：

**文件名：(id).json**

**内容：**

`{"id":(str),"time":(str),"detail":[{"quesion":(str),"user_answer":(str),"correct_answer":(str),"reault":(int,0表错误/1表正确)},{},.....]}`