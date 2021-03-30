import os

from conans import ConanFile, CMake, tools

channel = "stable"
username = "zyq"

class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package_multi"
    requires = "qhull/2015.2@%s/%s" % (username, channel)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["QHULL_REENTRANT"] = True
        cmake.definitions["QHULL_SHARED"] = True
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path, run_environment=True)
