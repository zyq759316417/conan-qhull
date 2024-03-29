import os

from conans import ConanFile, CMake, tools

class QhullConan(ConanFile):
    name = "qhull"
    description = "Qhull computes the convex hull, Delaunay triangulation, " \
                  "Voronoi diagram, halfspace intersection about a point, " \
                  "furthest-site Delaunay triangulation, and furthest-site " \
                  "Voronoi diagram."
    license = "Qhull"
    topics = ("conan", "qhull", "geometry", "convex", "triangulation", "intersection")
    homepage = "http://www.qhull.org"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "reentrant": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": False,
        "reentrant": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.options.reentrant

    def source(self):
        self.printInfo("before source")
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)
        self.printInfo("after source")


    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        self.printInfo("before build")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()
        self.printInfo("after build")



    def package(self):
        self.printInfo("before package")
        self.copy("COPYING.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "doc"))
        tools.rmdir(os.path.join(self.package_folder, "man"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.printInfo("after package")

    def package_info(self):
        self.printInfo("before package info")
        self.cpp_info.names["cmake_find_package"] = "Qhull"
        self.cpp_info.names["cmake_find_package_multi"] = "Qhull"
        self.cpp_info.components["libqhull"].names["cmake_find_package"] = self._qhull_cmake_name
        self.cpp_info.components["libqhull"].names["cmake_find_package_multi"] = self._qhull_cmake_name
        self.cpp_info.components["libqhull"].names["pkg_config"] = self._qhull_pkgconfig_name
        self.cpp_info.components["libqhull"].libs = [self._qhull_lib_name]
        if self.settings.os == "Linux":
            self.cpp_info.components["libqhull"].system_libs.append("m")
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            self.cpp_info.components["libqhull"].defines.extend(["qh_dllimport"])

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.printInfo("after package info")

    @property
    def _qhull_cmake_name(self):
        name = ""
        if self.options.reentrant:
            name = "qhull_r" if self.options.shared else "qhullstatic_r"
        else:
            name = "libqhull" if self.options.shared else "qhullstatic"
        return name

    @property
    def _qhull_pkgconfig_name(self):
        name = "qhull"
        if not self.options.shared:
            name += "static"
        if self.options.reentrant:
            name += "_r"
        return name

    @property
    def _qhull_lib_name(self):
        name = "qhull"
        if not self.options.shared:
            name += "static"
        if self.settings.build_type == "Debug" or self.options.reentrant:
            name += "_"
            if self.options.reentrant:
                name += "r"
            if self.settings.build_type == "Debug":
                name += "d"
        return name

    def printInfo(self, name):
        print("---------------------------%s method-----------------------------" % (name))
        print("name: " + str(self.name))
        print("settings: " + str(self.settings))
        print("options: " + str(self.options))
        print("exports: " + str(self.exports))
        print("install_folder: " + str(self.install_folder))
        print("build_folder: " + str(self.build_folder))
        print("package_folder: " + str(self.package_folder))
        print("recipe_folder: " + str(self.recipe_folder))
        print("source_folder: " + str(self.source_folder))
        # print("conan_data: " + str(self.conan_data))
        print("exports_sources: " + str(self.exports_sources))
