#!/usr/bin/env python3
"""Offline regression tests for the convention guard and shipped Java test examples.

Input: local checker and repository examples. Output: unittest results, nonzero on
failure. Writes only isolated temporary Java fixtures; no network or credentials.
"""

import re
import tempfile
import unittest
from pathlib import Path

from check_wind_conventions import check_test_method_names, run


class InterfaceDependencyTests(unittest.TestCase):
    def scan(self, consumer, *, test=False, implementation=None, extras=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = {
                "main/api/OrderService.java": "package api; public interface OrderService {}",
                "main/impl/OrderServiceImpl.java": implementation or (
                    "package impl; import api.OrderService; "
                    "public class OrderServiceImpl implements OrderService {}"
                ),
                ("test" if test else "main") + "/client/Client.java": consumer,
                **(extras or {}),
            }
            for name, source in sources.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source, encoding="utf-8")
            return [item for item in run(root, profile="java") if "依赖接口" in item.message]

    def testRejectImplementationFieldAndConstructor(self):
        findings = self.scan("""package client;
import impl.OrderServiceImpl;
class Client {
    private final OrderServiceImpl orders;
    Client(OrderServiceImpl orders) { this.orders = orders; }
}
""")
        self.assertEqual([4, 5], [item.line_no for item in findings])
        self.assertTrue(all(item.severity == "ERROR" for item in findings))

    def testResolveQualifiedAndSamePackageTypes(self):
        for consumer in (
            "package client; class Client { private impl.OrderServiceImpl orders; }",
            "package impl; class Client { private OrderServiceImpl orders; }",
        ):
            with self.subTest(consumer=consumer):
                self.assertEqual(1, len(self.scan(consumer)))

    def testAcceptInterfaceConsumer(self):
        self.assertEqual([], self.scan("""package client;
import api.OrderService;
class Client {
    private final OrderService orders;
    Client(OrderService orders) { this.orders = orders; }
}
"""))

    def testDoNotInventAnInterfaceFromSuffix(self):
        self.assertEqual([], self.scan(
            "package client; import impl.OrderServiceImpl; class Client { private OrderServiceImpl value; }",
            implementation="package impl; public class OrderServiceImpl {}",
        ))

    def testDoNotConfuseImportedSameNameOrNestedType(self):
        for consumer in (
            "package client; import other.OrderServiceImpl; class Client { private OrderServiceImpl value; }",
            "package client; class Client { static class OrderServiceImpl {} private OrderServiceImpl value; }",
        ):
            with self.subTest(consumer=consumer):
                self.assertEqual([], self.scan(consumer, extras={
                    "main/other/OrderServiceImpl.java": "package other; public class OrderServiceImpl {}",
                }))

    def testSkipAmbiguousSourceAndUnresolvedContracts(self):
        consumer = "package client; import impl.OrderServiceImpl; class Client { private OrderServiceImpl value; }"
        self.assertEqual([], self.scan(consumer, extras={
            "other/main/impl/OrderServiceImpl.java": "package impl; public class OrderServiceImpl {}",
        }))
        self.assertEqual([], self.scan(consumer, implementation=(
            "package impl; import external.OrderService; "
            "public class OrderServiceImpl implements OrderService {}"
        )))

    def testAcceptAssemblyAndPureImplementationUnitTest(self):
        assembly = """package client;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Bean;
import impl.OrderServiceImpl;
import api.OrderService;
@Configuration
class Client {
    @Bean OrderService orders() { return new OrderServiceImpl(); }
}
"""
        self.assertEqual([], self.scan(assembly))
        self.assertEqual([], self.scan(
            "package client; import impl.OrderServiceImpl; class Client { private OrderServiceImpl subject; }",
            test=True,
        ))

    def testSpringContractTestUsesInterface(self):
        self.assertEqual(1, len(self.scan("""package client;
import org.springframework.beans.factory.annotation.Autowired;
import impl.OrderServiceImpl;
class Client {
    @Autowired private OrderServiceImpl orders;
}
""", test=True)))

    def testIgnoreCommentsAndStrings(self):
        self.assertEqual([], self.scan('''package client;
import impl.OrderServiceImpl;
class Client {
    // private OrderServiceImpl orders;
    String example = "private OrderServiceImpl orders;";
}
'''))


class JavaTestExampleTests(unittest.TestCase):
    def testShippedSpringExamplesFollowTestNaming(self):
        root = Path(__file__).resolve().parents[2]
        reference = root / "senior-software-architect/references"
        checked = 0
        for name in ("service-flow", "web", "spring-common"):
            source = reference / f"testing-practices-java-{name}.md"
            for block in re.findall(r"```java\n(.*?)```", source.read_text(), re.DOTALL):
                findings = check_test_method_names(root / "test/ExampleTest.java", root, block)
                self.assertEqual([], findings, source.name)
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
