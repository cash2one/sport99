/**
 * Created by zhaojm on 4/24/16.
 */
Array.prototype.indexOf = Array.prototype.indexOf || function (searchElement, fromIndex) {
        if (this === undefined || this === null) {
            throw new TypeError('"this" is null or not defined');
        }

        var length = this.length >>> 0; // Hack to convert object.length to a UInt32

        fromIndex = +fromIndex || 0;

        if (Math.abs(fromIndex) === Infinity) {
            fromIndex = 0;
        }

        if (fromIndex < 0) {
            fromIndex += length;

            if (fromIndex < 0) {
                fromIndex = 0;
            }
        }

        for (; fromIndex < length; fromIndex++) {
            if (this[fromIndex] === searchElement) {
                return fromIndex;
            }
        }

        return -1;
    };

Array.prototype.clear = Array.prototype.clear || function () {
        this.length = 0;
    };

Array.prototype.insertAt = Array.prototype.insertAt || function (index, obj) {
        this.splice(index, 0, obj);
    };

Array.prototype.removeAt = Array.prototype.removeAt || function (index) {
        this.splice(index, 1);
    };

Array.prototype.remove = Array.prototype.remove || function (obj) {
        var index = this.indexOf(obj);
        if (index >= 0) {
            this.removeAt(index);
        }
    };