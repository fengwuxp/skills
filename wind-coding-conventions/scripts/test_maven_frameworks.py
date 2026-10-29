#!/usr/bin/env python3
"""离线验证 Maven 依赖继承边界，仅写入临时 fixture；失败返回非零，不联网。"""

import tempfile
import unittest
from pathlib import Path

from check_wind_conventions import module_frameworks


DEPENDENCIES = """<dependencies>
<dependency><groupId>org.springframework</groupId><artifactId>spring-context</artifactId></dependency>
<dependency><groupId>org.projectlombok</groupId><artifactId>lombok</artifactId></dependency>
</dependencies>"""


class MavenFrameworkTests(unittest.TestCase):
    def scan(self, parent_xml="", *, parent_path="pom.xml", parent_group="example", source=""):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / parent_path
            parent.parent.mkdir(parents=True, exist_ok=True)
            parent.write_text(f"<project><groupId>{parent_group}</groupId><artifactId>parent</artifactId>"
                              f"<version>1</version>{DEPENDENCIES}</project>", encoding="utf-8")
            module = root / "module"
            module.mkdir()
            (module / "pom.xml").write_text(f"<project>{parent_xml}<artifactId>child</artifactId></project>", encoding="utf-8")
            java = module / "src/main/java/LocalServiceImpl.java"
            java.parent.mkdir(parents=True)
            java.write_text(source + "\npublic class LocalServiceImpl {}", encoding="utf-8")
            return module_frameworks(java, root), module_frameworks(java, module)

    def parent(self, relative=None):
        path = "" if relative is None else f"<relativePath>{relative}</relativePath>"
        return f"<parent><groupId>example</groupId><artifactId>parent</artifactId><version>1</version>{path}</parent>"

    def testAggregationDoesNotInheritDependencies(self):
        self.assertEqual(((False, False), (False, False)), self.scan())

    def testActualParentInheritsForEitherScanRoot(self):
        self.assertEqual(((True, True), (True, True)), self.scan(self.parent()))

    def testExplicitParentOutsideModuleDirectory(self):
        self.assertEqual(((True, True), (True, True)),
                         self.scan(self.parent("../config/base.xml"), parent_path="config/base.xml"))

    def testEmptyRelativePathDoesNotUseDirectoryParent(self):
        self.assertEqual(((False, False), (False, False)), self.scan(self.parent("")))

    def testMismatchedParentCoordinatesRemainUnknown(self):
        self.assertEqual(((False, False), (False, False)), self.scan(self.parent(), parent_group="other"))

    def testMissingParentDoesNotGuess(self):
        self.assertEqual(((False, False), (False, False)), self.scan(self.parent("../missing.xml")))

    def testSourceImportRemainsEvidence(self):
        self.assertEqual(((True, False), (True, False)),
                         self.scan(source="import org.springframework.stereotype.Service;"))


if __name__ == "__main__":
    unittest.main()
