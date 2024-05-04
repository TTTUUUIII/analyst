### 1. 支持情况

|类型   |说明    |可用状态                     |
|-------|--------|----------------------------|
|1      |等高线图|<font color=green>YES</font>|
|2      |折线图  |<font color=red>NO</font>   |
|3      |条形图  |<font color=red>NO</font>   |
|4      |饼图    |<font color=red>NO</font>   |
|5      |散点图  |<font color=red>NO</font>   |
|6      |雷达图  |<font color=red>NO</font>   |

### 2. 绘图说明对象

#### 2.1 等高线图

```json
  {
    "type": 1,
    "ctx": {
      "data": pass,
      "row": pass,
      "col": pass,
      "transpose": pass,
      "remap": pass
    }
  }
```
其中：
```txt
> `data`            `array`    一维或二维数组
> `row`             `int`     指明数据有多少行（一维）
> `col`             `int`     指明数据有多少列（一维）
> `remap`           `bool`    指明数据是否需要重映射
> `transpose`       `bool`    指明数据是否需要转置处理
```
