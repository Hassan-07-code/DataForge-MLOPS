export function formatFileSize(bytes) {
    if (!bytes) {
        return "0 Bytes";
    }

    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB",
    ];

    const index = Math.floor(
        Math.log(bytes)
        / Math.log(1024)
    );

    const size =
        bytes / (1024 ** index);

    return (
        `${size.toFixed(2)} `
        + units[index]
    );
}
