# toolchain/avr.bzl
# Taken from https://retrylife.ca/blog/2020/09/03/bazel-and-avr

load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "ACTION_NAMES")
load(
    "@bazel_tools//tools/cpp:cc_toolchain_config_lib.bzl",
    "feature",
    "flag_group",
    "flag_set",
    "tool_path",
)


all_link_actions = [
    ACTION_NAMES.cpp_link_executable,
    ACTION_NAMES.cpp_link_dynamic_library,
    ACTION_NAMES.cpp_link_nodeps_dynamic_library,
]

tool_paths = [
    tool_path(
        name = "gcc",
        path = "/usr/local/bin/avr-gcc",
    ),
    tool_path(
        name = "ld",
        path = "/usr/local/bin/avr-ld",
    ),
    tool_path(
        name = "ar",
        path = "/usr/local/bin/avr-ar",
    ),
    tool_path(
        name = "cpp",
        path = "/usr/local/bin/avr-g++",
    ),
    tool_path(
        name = "gcov",
        path = "/usr/local/bin/avr-gcov",
    ),
    tool_path(
        name = "nm",
        path = "/usr/local/bin/avr-nm",
    ),
    tool_path(
        name = "objdump",
        path = "/usr/local/bin/avr-objdump",
    ),
    tool_path(
        name = "strip",
        path = "/usr/local/bin/avr-strip",
    ),
]

def _avr_impl(ctx):
    features = [
        feature(
            name = "default_linker_flags",
            enabled = True,
            flag_sets = [
                flag_set(
                    actions = all_link_actions,
                    flag_groups = ([
                        flag_group(
                            flags = [
                                "-lstdc++",
                            ],
                        ),
                    ]),
                ),
            ],
        ),
    ]

    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        toolchain_identifier = "avr-toolchain",
        host_system_name = "local",
        target_system_name = "local",
        target_cpu = "avr",
        target_libc = "unknown",
        compiler = "avr-g++",
        abi_version = "unknown",
        abi_libc_version = "unknown",
        tool_paths = tool_paths,
        cxx_builtin_include_directories = [
            "/usr/lib/avr/include",
            "/usr/lib/gcc/avr/5.4.0/include"
        ],
    )

cc_toolchain_config = rule(
    attrs = {},
    provides = [CcToolchainConfigInfo],
    implementation = _avr_impl,
)
