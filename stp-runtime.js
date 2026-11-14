/*
 * Salve o Tricolor Paulista — renderizador do site.
 * Lê o modelo em <template id="stp-modelo"> e o desenha com os valores de
 * Component.renderVals(). Entende {{campo}}, <sc-if value>, <sc-for list as>
 * e eventos onClick / onChange.
 */
(function () {
  "use strict";

  function DCLogic(props) { this.props = props || {}; this.state = {}; }
  DCLogic.prototype.setState = function (parcial) {
    var muda = typeof parcial === "function" ? parcial(this.state) : parcial;
    this.state = Object.assign({}, this.state, muda);
    agendar();
  };
  window.DCLogic = DCLogic;

  var SVG = "http://www.w3.org/2000/svg";
  var BURACO = /\{\{\s*([^}]+?)\s*\}\}/g;
  var INTEIRO = /^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/;
  var EVENTOS = { onclick: "click", onchange: "input", oninput: "input", onsubmit: "submit", onkeydown: "keydown" };

  var comp, modelo, raiz, pendente = false;

  function valor(expr, escopos) {
    expr = expr.trim();
    if (expr === "true") return true;
    if (expr === "false") return false;
    var partes = expr.split(".");
    var base;
    for (var i = escopos.length - 1; i >= 0; i--) {
      if (escopos[i] && Object.prototype.hasOwnProperty.call(escopos[i], partes[0])) { base = escopos[i][partes[0]]; break; }
    }
    for (var j = 1; j < partes.length && base != null; j++) base = base[partes[j]];
    return base;
  }
  function texto(str, escopos) {
    return str.replace(BURACO, function (_, e) { var v = valor(e, escopos); return v == null ? "" : String(v); });
  }

  function desenhar(no, pai, escopos, emSvg) {
    if (no.nodeType === 3) { pai.appendChild(document.createTextNode(texto(no.nodeValue, escopos))); return; }
    if (no.nodeType !== 1) return;
    var tag = no.tagName.toLowerCase();
    var filhos = (no.content || no).childNodes;
    if (tag === "sc-if") {
      var m = INTEIRO.exec(no.getAttribute("value") || "");
      if (m && valor(m[1], escopos)) for (var a = 0; a < filhos.length; a++) desenhar(filhos[a], pai, escopos, emSvg);
      return;
    }
    if (tag === "sc-for") {
      var ml = INTEIRO.exec(no.getAttribute("list") || "");
      var lista = ml ? valor(ml[1], escopos) : null, nome = no.getAttribute("as") || "item";
      (lista || []).forEach(function (item, i) {
        var esc = {}; esc[nome] = item; esc[nome + "Index"] = i;
        var novos = escopos.concat([esc]);
        for (var b = 0; b < filhos.length; b++) desenhar(filhos[b], pai, novos, emSvg);
      });
      return;
    }
    var svg = emSvg || tag === "svg";
    var el = svg ? document.createElementNS(SVG, no.tagName) : document.createElement(tag);
    for (var k = 0; k < no.attributes.length; k++) {
      var at = no.attributes[k], n = at.name, v = at.value;
      if (n.indexOf("hint-") === 0) continue;
      var ev = EVENTOS[n.toLowerCase()];
      if (ev) {
        var mf = INTEIRO.exec(v), fn = mf ? valor(mf[1], escopos) : null;
        if (typeof fn === "function") el.addEventListener(ev, fn);
        continue;
      }
      var mi = INTEIRO.exec(v);
      if (mi) {
        var val = valor(mi[1], escopos);
        if (n === "value" && "value" in el) { el.value = val == null ? "" : val; continue; }
        if (val === false || val == null) continue;
        el.setAttribute(n, val === true ? "" : String(val));
      } else {
        el.setAttribute(n, texto(v, escopos));
      }
    }
    for (var c = 0; c < filhos.length; c++) desenhar(filhos[c], el, escopos, svg);
    pai.appendChild(el);
  }

  function render() {
    pendente = false;
    var foco = document.activeElement, idFoco = foco && foco.id, ini, fim;
    try { ini = foco.selectionStart; fim = foco.selectionEnd; } catch (e) {}
    var vals = comp.renderVals();
    var frag = document.createDocumentFragment();
    var nos = modelo.content.childNodes;
    for (var i = 0; i < nos.length; i++) desenhar(nos[i], frag, [vals], false);
    raiz.replaceChildren(frag);
    if (idFoco) {
      var novo = document.getElementById(idFoco);
      if (novo) { novo.focus(); try { if (ini != null) novo.setSelectionRange(ini, fim); } catch (e) {} }
    }
  }
  function agendar() { if (!pendente && comp) { pendente = true; requestAnimationFrame(render); } }

  window.addEventListener("DOMContentLoaded", function () {
    modelo = document.getElementById("stp-modelo");
    raiz = document.getElementById("stp-raiz");
    var C = (typeof Component !== "undefined") ? Component : window.Component;
    comp = new C({});
    render();
    if (location.hash) {
      var alvo = document.getElementById(location.hash.slice(1));
      if (alvo) setTimeout(function () { alvo.scrollIntoView(); }, 50);
    }
  });
})();
