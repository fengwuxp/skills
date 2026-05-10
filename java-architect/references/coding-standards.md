# 编码规范（阿里巴巴 Java 开发手册核心条款 + 项目补充）

## 命名规范（强制）

- 代码中的命名均不能以下划线或美元符号开始/结束。
- 严禁使用拼音与英文混合的方式，更不允许直接使用中文。
- 类名使用 `UpperCamelCase`，但 DO/BO/DTO/VO/AO/PO/UID 等除外。
- 方法名、参数名、成员变量、局部变量使用 `lowerCamelCase`。
- 常量命名全部大写，单词间用下划线隔开（如 `MAX_STOCK_COUNT`）。
- 抽象类命名使用 `Abstract` 或 `Base` 开头；异常类命名使用 `Exception` 结尾；测试类命名以它要测试的类名开头，以 `Test` 结尾。
- POJO 类中布尔类型变量都不要加 `is` 前缀（如用 `success` 而非 `isSuccess`）。
- 如果模块/接口/类/方法使用了设计模式，在命名时需体现出具体模式。

## 常量定义
- 【强制】不允许任何魔法值（即未经预先定义的常量）直接出现在代码中。
- 【强制】long或者Long初始赋值时，使用大写的L，不能是小写的l，小写容易跟数字1混淆，造成误解。
- 【推荐】不要使用一个常量类维护所有常量，按常量功能进行归类，分开维护。
     说明：大而全的常量类，非得使用查找功能才能定位到修改的常量，不利于理解和维护。
     正例：缓存相关常量放在类CacheConsts下；系统配置相关常量放在类ConfigConsts下。
- 【推荐】常量的复用层次有五层：跨应用共享常量、应用内共享常量、子工程内共享常量、包内共享常量、类内共享常量。
  (1） 跨应用共享常量：放置在二方库中，通常是client.jar中的constant目录下。
  (2） 应用内共享常量：放置在一方库中，通常是子模块中的constant目录下。
   反例：易懂变量也要统一定义成应用内共享常量，两位攻城师在两个类中分别定义了表示“是”的变量：
```text
  类A中：public static final String YES = "yes";
    类B中：public static final String YES = "y";
    A.YES.equals(B.YES) 预期是true，但实际返回为false，导致线上问题。
```
   (3） 子工程内部共享常量：即在当前子工程的constant目录下。
   (4） 包内共享常量：即在当前包下单独的constant目录下。
   (5） 类内共享常量：直接在类内部private static final定义。
- 【推荐】如果变量值仅在一个固定范围内变化用enum类型来定义。 说明：如果存在名称之外的延伸属性使用enum类型，下面正例中的数字就是延伸信息，表示一年中的第几个季节。

## OOP 规约（强制）

- 所有覆写方法，必须加 `@Override` 注解。
- 禁止使用过时的类或方法（deprecated）。
- 禁止使用 Java 标准库中的过时集合类（`Vector`、`Hashtable`、`Stack`），使用 `ArrayList`、`HashMap` 等替代。
- 禁止使用 `BigDecimal` 的构造方法 `new BigDecimal(double)`，应使用 `BigDecimal.valueOf(double)` 或 `new BigDecimal(String)`。
- 外部正在调用或者二方库依赖的接口，不允许修改方法签名。

## 集合处理（强制）

- 判断集合元素是否为空，使用 `isEmpty()` 而非 `size() == 0`。
- 使用 `Arrays.asList()` 转换的数组不能使用 `add`/`remove`/`clear` 方法。
- 不要在 `foreach` 循环里进行元素的 `remove`/`add`，应使用 `Iterator`。
- `ArrayList` 的 `subList` 结果不可强转成 `ArrayList`。

## 并发处理（强制）

- 获取单例对象需要保证线程安全。
- 线程资源必须通过线程池提供，不允许自行显式创建线程。
- `SimpleDateFormat` 是线程不安全的，定义为 `static` 必须加锁，或使用 `DateTimeFormatter` 替代。
- 高并发时，优先用无锁数据结构，锁区块尽量小。

## 编码原则
- 【强制】测试和实现只能依赖接口已经声明的能力；需要新字段时，先补接口契约，再补实现和测试。
- 【强制】类型引用优先：import：字段、方法参数、返回值、泛型、局部变量中不要直接写全限定类名，除非存在无法避免的同名冲突。
- 【强制】注解作用域要清晰：普通字段、参数、返回值使用 import 后的 @Nullable / @NonNull；只有 type-use 位置存在作用域歧义时，才允许用 @org.jspecify.annotations.Nullable 明确标注。
- 【强制】测试代码同样遵守生产代码规范：mock、匿名类、测试辅助类也不能把全限定类名当临时写法。
- 【强制】值对象和行为接口不能混用：看到 Spec、DTO、Request 先确认它是数据模型还是函数式能力，不要把普通类写成 lambda。
- 【强制】接口变更必须闭环，例如：Spec 字段 -> Assembler 填充 -> MapStruct 转换 -> Entity 落库 -> 测试断言 必须一次性串起来。
- 【强制】clean 验证：接口、重命名、注解、测试支撑类变更后，必须跑 clean test-compile，不能信 Maven 增量结果。

## 代码格式（强制）

- `if`/`for`/`while`/`switch`/`do` 等保留字与括号之间必须有空格。
- 二目、三目运算符左右两边加空格。
- 注释的双斜线与注释内容之间有且仅有一个空格。
- 单行字符数不超过 120 个。
- 所有覆写方法必须加 `@Override` 注解。
- 对于超过 5 个参数的公有方法应抽取 DTO 对象（如 `XxxRequest`）。

## 异常与日志（强制）

- 不要捕获 `RuntimeException` 的子类（如 `IndexOutOfBoundsException`、`NullPointerException`），由代码检查来规避。
- 事务场景中如果异常被捕获，要注意手动回滚；或在 `catch` 块中重新抛出异常。
- 禁止直接使用 `e.printStackTrace()`，必须使用日志框架（SLF4J + Logback）。
- 日志命名遵循 `logger` 或 `LOG` 作为统一命名。

### 日志打印示例

- INFO: `logger.info("Processing trade with id : {} and symbol : {}", id, symbol);`
- ERROR: `logger.error("handled xxx error, xxx : {}, message : {}", id, exception.getMessage(), exception);`
- 错误日志必须输出错误消息和异常堆栈。

## 数据库规约（强制）

- 表名、字段名必须使用小写字母或数字，禁止数字开头，禁止两个下划线中间只出现数字。
- 表达是与否概念的字段，使用 `is_xxx` 命名，数据类型为 `unsigned tinyint`（1 是，0 否）。
- 表必备三个字段：`id`、`create_time`、`update_time`。
- 禁止使用外键与级联更新/删除，一切外键概念在应用层解决。
- 业务唯一约束必须使用数据库唯一键约束。
- 新增字段如果为必填，必须有默认值，否则字段要可空。

### 通用表字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | bigint(20) | 主键（强制） |
| `gmt_create` | datetime | 创建时间（强制） |
| `gmt_modified` | datetime | 最后更新时间（强制） |
| `creator` | - | 创建人（可选） |
| `modifier` | - | 修改人（可选） |
| `order_index` | int(11) | 排序（可选） |

## 项目级补充规范

### 模块包名结构
```text
具体模块下的包名按功能划分，例如：
-dal：数据库操作相关
--entities：实体类
--enums：和实体相关枚举
--mapper：mybatis plus mapper
-services 服务层
--impl：服务实现
--mapstruct: mapstruct 相关的 DTO Converter
--model：DTO 、Request 、Query 对象
---dto：
---request
---query
```

### CRUD 方法命名

- 不区分创建/更新：`saveXxx`
- 区分创建/更新：`createXxx` / `updateXxx`
- 分页/列表：`query{实体复数}`（如 `queryRoles`）
- 单个对象：`queryXxxById`（原则上不返回空，若可能为空需用 `@Nullable` 标注并断言）
- 删除：`deleteXxxById` / `deleteXxxByIds`

### 模型对象命名

- 请求对象（不区分）：`SaveXxxRequest`
- 区分：`CreateXxxRequest` / `UpdateXxxRequest`
- 查询对象：`XxxQuery`
- 枚举：实现 `DescriptiveEnum` 接口

### MyBatis Flex 最佳实践

- **禁止使用 `LambdaQueryWrapper`**，必须使用 `XxxRefs` 生成的字段常量类。
- 时间对象统一使用 `LocalDateTime`。
- 插入/更新方法选择：
    - `insertSelective` / `update` / `insertOrUpdateSelective` 推荐（忽略 null）
    - 需手动处理更新时间及空值场景。
- 查询排序：使用抽象基类 `AbstractPageQuery`，支持 `orderFields` + `orderTypes` 数组排序。

### 异常处理

- 异常应继承 `BaseException`。
- 优先使用 `AssertUtils` 进行断言（`notNull`、`hasText`、`isTrue` 等），减少 if 判断。
- Controller / API / ApplicationService 对外不允许暴露实体类型对象，应返回 DTO/VO/Result；DomainService 和基础服务可在模块内部使用实体。

### 测试规约

- 测试写在 `tests` 模块下，类名以 `Test` 结尾，方法以 `test` 开头。
- 包名与被测试类相同。
- 每个测试方法最少一个断言，建议一个方法只测试一个逻辑分支。
- 继承 `AbstractServiceTest` 按需加载 Spring 上下文。
- 使用 `@VisibleForTesting` 标注为测试而放宽可见性的方法。

### 依赖管理

- 根 pom 的 `dependencyManagement` 中统一声明所有依赖版本（包括第三方和项目自身模块）。子模块依赖时不再写版本号。