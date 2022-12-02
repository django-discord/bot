import black


def black_string(content):
    return black.format_str(
        src_contents=content,
        mode=black.Mode(
            target_versions={black.TargetVersion.PY36},
            line_length=80,
            string_normalization=False,
            is_pyi=False,
        ),
    )
