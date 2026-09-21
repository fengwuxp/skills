#!/usr/bin/env python3
"""Regression tests for high-confidence Java readability and Wind layering guards."""

import tempfile
import unittest
from pathlib import Path

from check_wind_conventions import check_nested_ternary_expressions, run


class ReadabilityBoundaryTests(unittest.TestCase):
    def write_source(self, root: Path, name: str, source: str) -> Path:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path

    def finding_shape(self, findings):
        return [(item.severity, item.path.as_posix(), item.line_no) for item in findings]

    def testRejectsPairedNestedTernaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_source(root, "src/main/java/sample/LabelPolicy.java", """package sample;
class LabelPolicy {
    String label(boolean dependency, boolean value, boolean active) {
        return dependency ? "ready" : value ? "missing" : active ? "active" : "inactive";
    }
}
""")

            findings = check_nested_ternary_expressions(path, root, path.read_text(encoding="utf-8"))

            self.assertEqual(
                [("ERROR", "src/main/java/sample/LabelPolicy.java", 4)] * 2,
                self.finding_shape(findings),
            )

    def testRejectsNestedParenthesizedFalseBranch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_source(root, "src/main/java/sample/Labels.java", """package sample;
class Labels {
    String label(boolean primary, boolean secondary) {
        return primary ? "primary" : (secondary ? "secondary" : "other");
    }
}
""")

            findings = check_nested_ternary_expressions(path, root, path.read_text(encoding="utf-8"))

            self.assertEqual(
                [("ERROR", "src/main/java/sample/Labels.java", 4)],
                self.finding_shape(findings),
            )

    def testRejectsNestedTrueBranch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_source(root, "src/main/java/sample/Labels.java", """package sample;
class Labels {
    String label(boolean primary, boolean secondary) {
        return primary ? (secondary ? "secondary" : "other") : "primary";
    }
}
""")

            findings = check_nested_ternary_expressions(path, root, path.read_text(encoding="utf-8"))

            self.assertEqual(
                [("ERROR", "src/main/java/sample/Labels.java", 4)],
                self.finding_shape(findings),
            )

    def testAcceptsSimpleAndIndependentParenthesizedTernariesAndGenericWildcards(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_source(root, "src/main/java/sample/Labels.java", """package sample;
import java.util.List;
class Labels {
    String choose(boolean first, boolean second) {
        List<? extends Number> values = List.of();
        return (first ? "first" : "other") + (second ? "second" : "other");
    }
}
""")

            findings = check_nested_ternary_expressions(path, root, path.read_text(encoding="utf-8"))

            self.assertEqual([], findings)

    def testIgnoresTernaryTokensInCommentsAndStrings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_source(root, "src/main/java/sample/Example.java", """package sample;
class Example {
    String text = "flag ? first : second ? third : fourth";
    // flag ? first : second ? third : fourth
    String label(boolean flag) { return flag ? "yes" : "no"; }
}
""")

            findings = check_nested_ternary_expressions(path, root, path.read_text(encoding="utf-8"))

            self.assertEqual([], findings)


class ControllerMapperBoundaryTests(unittest.TestCase):
    def write_sources(self, root: Path, sources: dict[str, str]) -> None:
        for name, source in sources.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(source, encoding="utf-8")

    def finding_shape(self, findings):
        return [(item.severity, item.path.as_posix(), item.line_no) for item in findings]

    def testWindRejectsControllerMapperFieldAndConstructor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_sources(root, {
                "src/main/java/sample/dal/mapper/OrderMapper.java": "package sample.dal.mapper; public interface OrderMapper {}",
                "src/main/java/sample/web/OrderController.java": """package sample.web;
import sample.dal.mapper.OrderMapper;
public class OrderController {
    private final OrderMapper orders;
    public OrderController(OrderMapper orders) { this.orders = orders; }
}
""",
            })

            findings = run(root, profile="wind")

            self.assertEqual(
                [
                    ("ERROR", "src/main/java/sample/web/OrderController.java", 4),
                    ("ERROR", "src/main/java/sample/web/OrderController.java", 5),
                ],
                self.finding_shape(findings),
            )

    def testWindRecognizesAnnotatedAndBaseMapperSources(self):
        mapper_sources = (
            """package sample.mapping;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface OrderMapper {}
""",
            """package sample.mapping;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
public interface OrderMapper extends BaseMapper<Order> {}
""",
        )
        for mapper_source in mapper_sources:
            with self.subTest(mapper_source=mapper_source), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_sources(root, {
                    "src/main/java/sample/mapping/OrderMapper.java": mapper_source,
                    "src/main/java/sample/web/OrderController.java": """package sample.web;
import sample.mapping.OrderMapper;
public class OrderController {
    private final OrderMapper orders;
    public OrderController(OrderMapper orders) { this.orders = orders; }
}
""",
                })

                findings = run(root, profile="wind")

                self.assertEqual(
                    [
                        ("ERROR", "src/main/java/sample/web/OrderController.java", 4),
                        ("ERROR", "src/main/java/sample/web/OrderController.java", 5),
                    ],
                    self.finding_shape(findings),
                )

    def testAllowsServiceAndServiceImplMapperDependency(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_sources(root, {
                "src/main/java/sample/dal/mapper/OrderMapper.java": "package sample.dal.mapper; public interface OrderMapper {}",
                "src/main/java/sample/service/OrderService.java": "package sample.service; public interface OrderService {}",
                "src/main/java/sample/service/impl/OrderServiceImpl.java": """package sample.service.impl;
import sample.dal.mapper.OrderMapper;
import sample.service.OrderService;
public class OrderServiceImpl implements OrderService {
    private final OrderMapper orders;
    public OrderServiceImpl(OrderMapper orders) { this.orders = orders; }
}
""",
                "src/main/java/sample/web/OrderController.java": """package sample.web;
import sample.service.OrderService;
public class OrderController {
    private final OrderService orders;
    public OrderController(OrderService orders) { this.orders = orders; }
}
""",
            })

            findings = run(root, profile="wind")

            self.assertEqual([], findings)

    def testJavaProfileDoesNotApplyWindControllerMapperRule(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_sources(root, {
                "src/main/java/sample/dal/mapper/OrderMapper.java": "package sample.dal.mapper; public interface OrderMapper {}",
                "src/main/java/sample/web/OrderController.java": """package sample.web;
import sample.dal.mapper.OrderMapper;
public class OrderController {
    private final OrderMapper orders;
    public OrderController(OrderMapper orders) { this.orders = orders; }
}
""",
            })

            findings = run(root, profile="java")

            self.assertEqual([], findings)

    def testAllowsConversionOrMapStructMapper(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_sources(root, {
                "src/main/java/sample/conversion/OrderMapper.java": """package sample.conversion;
import org.mapstruct.Mapper;
@Mapper
public interface OrderMapper {}
""",
                "src/main/java/sample/web/OrderController.java": """package sample.web;
import sample.conversion.OrderMapper;
public class OrderController {
    private final OrderMapper orders;
    public OrderController(OrderMapper orders) { this.orders = orders; }
}
""",
            })

            findings = run(root, profile="wind")

            self.assertEqual([], findings)

    def testAllowsMapperWithoutResolvedPersistenceSource(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_sources(root, {
                "src/main/java/sample/web/OrderController.java": """package sample.web;
import external.OrderMapper;
public class OrderController {
    private final OrderMapper orders;
    public OrderController(OrderMapper orders) { this.orders = orders; }
}
""",
            })

            findings = run(root, profile="wind")

            self.assertEqual([], findings)

    def testAllowsAmbiguousPersistenceMapperSource(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_sources(root, {
                "src/main/java/sample/dal/mapper/OrderMapper.java": "package sample.dal.mapper; public interface OrderMapper {}",
                "generated/main/java/sample/dal/mapper/OrderMapper.java": "package sample.dal.mapper; public interface OrderMapper {}",
                "src/main/java/sample/web/OrderController.java": """package sample.web;
import sample.dal.mapper.OrderMapper;
public class OrderController {
    private final OrderMapper orders;
    public OrderController(OrderMapper orders) { this.orders = orders; }
}
""",
            })

            findings = run(root, profile="wind")

            self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main()
