from conans import ConanFile, CMake, tools
import glob
import os


class XnnpackConan(ConanFile):
    name = "xnnpack"
    description = "XNNPACK is a highly optimized library of floating-point " \
                  "neural network inference operators for ARM, WebAssembly, " \
                  "and x86 platforms."
    license = "BSD-3-Clause"
    topics = ("conan", "xnnpack", "neural-network", "inference", "multithreading",
              "inference-optimization", "matrix-multiplication", "simd")
    homepage = "https://github.com/google/XNNPACK"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "assembly": [True, False],
        "memopt": [True, False],
        "sparse": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "assembly": True,
        "memopt": True,
        "sparse": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("cpuinfo/cci.20201217")
        self.requires("fp16/cci.20200514")
        self.requires("fxdiv/cci.20200417")
        self.requires("pthreadpool/cci.20210218")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("XNNPACK-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["XNNPACK_LIBRARY_TYPE"] = "default"
        self._cmake.definitions["XNNPACK_ENABLE_ASSEMBLY"] = self.options.assembly
        self._cmake.definitions["XNNPACK_ENABLE_MEMOPT"] = self.options.memopt
        self._cmake.definitions["XNNPACK_ENABLE_SPARSE"] = self.options.sparse
        self._cmake.definitions["XNNPACK_BUILD_TESTS"] = False
        self._cmake.definitions["XNNPACK_BUILD_BENCHMARKS"] = False
        self._cmake.definitions["XNNPACK_USE_SYSTEM_LIBS"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["XNNPACK"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
