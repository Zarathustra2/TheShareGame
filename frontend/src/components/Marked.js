import marked from 'marked';
import DOMPurify from 'dompurify';

export default {
  functional: true,

  name: 'MarkedComponent',

  props: {
    markdown: {
      type: String,
      default: '',
    },

    className: {
      type: String,
      default: 'marked-component',
    },

    options: {
      type: Object,
      default: () => ({}),
    },
  },

  render(createElement, context) {
    const markdown = context.props.markdown || (context.children && context.children.length > 0 ? context.children[0].text : '');
    const { className } = context.props;
    const { options } = context.props;
    const renderer = new marked.Renderer();

    renderer.link = (href, title, text) => `<a target="_blank" href="${href}" title="${title}">${text}</a>`;

    marked.setOptions(options);

    return createElement('div', {
      class: className,
      domProps: {
        innerHTML: DOMPurify.sanitize(marked(markdown, { renderer }), { ADD_ATTR: ['target'] }),
      },
    });
  },
};
