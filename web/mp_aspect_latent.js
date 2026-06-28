import { app } from "../../scripts/app.js";

// ---- Hide/show the mode-specific field --------------------------------------
// Fully collapse a widget (zero height, no draw) so it occupies no space and
// cannot overlap neighbours, while staying in node.widgets at the SAME index so
// saved values still restore by position and its value is still sent to the backend.
// IMPORTANT: never add or remove widgets here. Doing so shifts widgets_values on
// load and corrupts every field below the inserted widget.
function setWidgetVisible(node, widget, visible) {
    if (!widget) return;
    if (visible) {
        if (widget._mpalpHidden) {
            widget.type = widget._mpalpType;
            widget.computeSize = widget._mpalpComputeSize;
            widget.draw = widget._mpalpDraw;
            delete widget.hidden;
            delete widget._mpalpHidden;
        }
    } else if (!widget._mpalpHidden) {
        widget._mpalpType = widget.type;
        widget._mpalpComputeSize = widget.computeSize;
        widget._mpalpDraw = widget.draw;
        widget.type = "mpalp_hidden";
        widget.hidden = true;
        widget.computeSize = () => [0, 0];
        widget.draw = () => {};
        widget._mpalpHidden = true;
    }
}

// ---- Separator lines --------------------------------------------------------
// Drawn directly on the node canvas (NOT inserted as widgets), so they never
// affect serialization or widget indexing. A faint line is drawn just above each
// named widget to visually group the fields.
const SEPARATE_ABOVE = ["aspect_ratio", "width_override", "batch_size"];

function installSeparators(node) {
    const original = node.onDrawForeground;
    node.onDrawForeground = function (ctx) {
        original?.apply(this, arguments);
        if (this.flags?.collapsed || !this.widgets) return;
        ctx.save();
        ctx.strokeStyle =
            (typeof LiteGraph !== "undefined" && LiteGraph.WIDGET_OUTLINE_COLOR) || "#555";
        ctx.globalAlpha = 0.35;
        const margin = 14;
        for (const name of SEPARATE_ABOVE) {
            const w = this.widgets.find((x) => x.name === name);
            if (!w || w.last_y == null || w._mpalpHidden) continue;
            const y = w.last_y - 4;
            ctx.beginPath();
            ctx.moveTo(margin, y);
            ctx.lineTo(this.size[0] - margin, y);
            ctx.stroke();
        }
        ctx.restore();
    };
}

app.registerExtension({
    name: "MPAspectLatentPicker.ui",
    nodeCreated(node) {
        if (node.comfyClass !== "MPAspectLatentPicker") return;
        if (!node.widgets) return;

        installSeparators(node);

        const get = (name) => node.widgets.find((w) => w.name === name);
        const modeWidget = get("sizing_mode");
        if (!modeWidget) return;

        const refresh = () => {
            const isMP = modeWidget.value === "megapixels";
            setWidgetVisible(node, get("megapixels"), isMP);
            setWidgetVisible(node, get("scale"), !isMP);
            const computed = node.computeSize();
            node.setSize([Math.max(node.size[0], computed[0]), computed[1]]);
            node.setDirtyCanvas(true, true);
        };

        const originalCallback = modeWidget.callback;
        modeWidget.callback = function () {
            const result = originalCallback?.apply(this, arguments);
            refresh();
            return result;
        };

        requestAnimationFrame(refresh);
    },
});
