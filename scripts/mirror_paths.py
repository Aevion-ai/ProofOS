import pathlib


def resolve_src(raw: str, base_src_dir: pathlib.Path) -> tuple[pathlib.Path | None, str | None]:
    if not raw.strip():
        return None, "empty source path"

    path_obj = pathlib.Path(raw)
    if path_obj.is_absolute():
        return None, f"absolute source path rejected: {raw}"

    src_path = (base_src_dir / path_obj).resolve()

    if src_path == base_src_dir:
        return None, f"source resolves to checkout root: {raw}"

    if not src_path.is_relative_to(base_src_dir):
        return None, f"source path traversal detected: {raw}"

    if src_path.relative_to(base_src_dir).parts[0] == ".git":
        return None, f"source targets protected path: {raw}"

    return src_path, None

def resolve_dst(raw: str, base_dst_dir: pathlib.Path, base_src_dir: pathlib.Path) -> tuple[pathlib.Path | None, str | None]:
    if not raw.strip():
        return None, "empty destination path"

    path_obj = pathlib.Path(raw)
    if path_obj.is_absolute():
        return None, f"absolute destination path rejected: {raw}"

    dst_path = (base_dst_dir / path_obj).resolve()

    if dst_path == base_dst_dir:
        return None, f"destination resolves to checkout root: {raw}"

    if not dst_path.is_relative_to(base_dst_dir) or dst_path.is_relative_to(base_src_dir):
        return None, f"destination path traversal detected: {raw}"

    PROTECTED = {".git", ".github", ".jules"}
    if dst_path.relative_to(base_dst_dir).parts[0] in PROTECTED:
        return None, f"destination targets protected path: {raw}"

    return dst_path, None
