//------------------------------------------------------------------------------
// This file is part of MyDojo package (https://github.com/honzamach/mydojo).
//
// Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
// Use of this source is governed by the MIT license, see LICENSE file.
//------------------------------------------------------------------------------

// Global application module.
var MyDojo = (function () {

    function _build_param_builder(skeleton, rules) {
        //var _skeleton = Object.assign({}, skeleton);
        var _skeleton = skeleton;
        var _rules = rules;
        return function(value) {
            //var _result = Object.assign({}, _skeleton);
            var _result = _skeleton;
            _rules.forEach(function(r) {
                _result[r[0]] = value;
            });
            return _result;
        }
    }

    var _csag = {
    };

    return {
        get_csags: function() {
            return _csag;
        },

        get_csag: function(name) {
            try {
                return _csag[name];
            }
            catch (err) {
                return null
            }
        }
    };
})();
