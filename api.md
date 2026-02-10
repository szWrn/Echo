注：本文档`（xx）`用于指示数据类型及格式，`......`表省略

### /get_index/

**请求方法：GET**

**返回格式：**

`{"data":["id":(int),"time":(str,"hh:mm:ss YY-MM-DD"),"type":(int)],[],....}`

\["data"]\[x]\["id"] -> 训练id

\["data"]\[x]\["time"] -> 训练时间

\["data"]\[x]\["type"] -> 训练类型（0：人机对话，1：具体发音训练，2：听声辩位）

### /get_report/

**请求方法：POST**

**请求体：**

`{“id”: (int)}`

id -> 要获取的训练id（由get_index获取）

**返回格式：**

`{"data":[{"question":(str),"user_answer":(str),"correct_answer":(str),"result":(int,0or1)},{},.....]}`

\["data"]\[x]\["question"] -> 问题

\["data"]\[x]\["user_answer"] -> 用户回答

\["data"]\[x]\["question"] -> 正确答案

\["data"]\[x]\["question"] -> 结果（0：错误，1：正确）

**get_report的返回格式将根据训练类型（get_report不提供训练类型数据，训练数据从get_index获取）适当删减或更改，其规则如下：**

**1.对于type = 0(人机对话训练)**

​	user_answer -> 用户对话

​	correct_answer -> AI对话（**此处不再代表正确答案！**）

​	**其余为空字符串**

**2.对于type = 1(具体发音训练)**

​	维持原有定义不变

**3.对于type = 2(听声辩位)**

​	question -> 空字符串省略

​	其余字段不变

