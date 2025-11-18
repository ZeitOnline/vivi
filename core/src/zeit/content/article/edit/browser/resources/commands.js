(function () {
  zeit.cms.declare_namespace('zeit.content.article.commands');

  // Orchestrates the conversion between paragraphs and lists (both directions).
  // Chrome has a bug where execCommand('insertunorderedlist') on a <p> element
  // creates invalid HTML (<ul> inside <p>). The browser auto-corrects this by
  // moving the <ul> outside the <p>, which removes the list entirely.
  // We work around this by manually manipulating the DOM instead of using execCommand.
  zeit.content.article.commands.insert_list = function(listType, editableElement) {
    var self = this;
    var selection = window.getSelection();
    if (!selection.rangeCount) {
      log('No selection for list toggle');
      return;
    }
    var range = selection.getRangeAt(0);
    var blocks = zeit.content.article.commands.get_selected_blocks(range, editableElement);
    if (blocks.length === 0) {
      return;
    }

    if (zeit.content.article.commands.all_blocks_are_lists(blocks)) {
      zeit.content.article.commands.convert_lists_to_paragraphs(blocks);
    } else {
      zeit.content.article.commands.convert_blocks_to_list(blocks, listType, range);
    }
  };

  // Finds the block-level element (P, DIV, UL, OL) that is a direct child of
  // the editable container and contains the given node.
  zeit.content.article.commands.find_editable_block = function(node, editable) {
    while (node && node !== editable) {
      if (zeit.content.article.commands.is_block_element(node, editable)) {
        return node;
      }
      node = node.parentNode;
    }
    return null;
  };

  // Checks if a node is a block element that can be converted to/from a list.
  // Only considers elements that are direct children of the editable container.
  zeit.content.article.commands.is_block_element = function(node, editable) {
    if (node.parentNode !== editable) {
      return false;
    }
    var blockTypes = ['P', 'DIV', 'UL', 'OL'];
    return blockTypes.indexOf(node.nodeName) !== -1;
  };

  // Collects all block elements within the selection range.
  // This handles both single-block and multi-block selections.
  zeit.content.article.commands.get_selected_blocks = function(range, editableElement) {
    var startContainer = range.startContainer;
    var endContainer = range.endContainer;

    // Text nodes need to be converted to their parent element nodes
    if (startContainer.nodeType === Node.TEXT_NODE) {
      startContainer = startContainer.parentNode;
    }
    if (endContainer.nodeType === Node.TEXT_NODE) {
      endContainer = endContainer.parentNode;
    }

    var startBlock = zeit.content.article.commands.find_editable_block(startContainer, editableElement);
    var endBlock = zeit.content.article.commands.find_editable_block(endContainer, editableElement);

    if (!startBlock || !endBlock) {
      log('Could not find start or end block');
      return [];
    }

    var blocks = [];
    var current = startBlock;
    while (current) {
      if (zeit.content.article.commands.is_block_element(current, editableElement)) {
        blocks.push(current);
      }
      if (current === endBlock) {
        break;
      }
      current = current.nextSibling;
    }

    return blocks;
  };

  // This is used to decide whether to toggle lists on or off.
  zeit.content.article.commands.all_blocks_are_lists = function(blocks) {
    return blocks.every(function(block) {
      return block.nodeName === 'UL' || block.nodeName === 'OL';
    });
  };

  // All <li> items become a single <p> with <br> tags separating the former list items.
  // This is should be the same behaviour as calling the original command.
  zeit.content.article.commands.convert_lists_to_paragraphs = function(blocks) {
    forEach(blocks, function(block) {
      var items = block.querySelectorAll('li');
      var p = MochiKit.DOM.createDOM('p');
      var isFirst = true;

      forEach(items, function(li) {
        // Add line break before each item except the first
        if (!isFirst) {
          p.appendChild(MochiKit.DOM.createDOM('br'));
        }
        isFirst = false;

        // Move all content from the list item into the paragraph
        while (li.firstChild) {
          p.appendChild(li.firstChild);
        }
      });

      // Replace the list with the single paragraph
      block.parentNode.insertBefore(p, block);
      MochiKit.DOM.removeElement(block);
    });
  };

  // Each block becomes a <li> item.
  // Existing lists have their items extracted and merged into the new list.
  zeit.content.article.commands.convert_blocks_to_list = function(blocks, listType, range) {
    var list = MochiKit.DOM.createDOM(listType);
    var firstBlock = blocks[0];

    // Process each block and add it as a list item
    forEach(blocks, function(block) {
      var items = zeit.content.article.commands.extract_list_items_from_block(block, listType);
      forEach(items, function(li) {
        list.appendChild(li);
      });
    });

    // Replace first block with the new list, remove the rest
    firstBlock.parentNode.replaceChild(list, firstBlock);
    for (var i = 1; i < blocks.length; i++) {
      if (blocks[i].parentNode) {
        MochiKit.DOM.removeElement(blocks[i]);
      }
    }
  };

  // Extracts or creates list items from a block element. If the block is already
  // a list, returns its <li> elements. Otherwise, wraps the block content in a new <li>.
  zeit.content.article.commands.extract_list_items_from_block = function(block, listType) {
    if (block.nodeName === 'UL' || block.nodeName === 'OL') {
      var existingItems = block.querySelectorAll('li');
      var clonedItems = [];
      forEach(existingItems, function(li) {
        clonedItems.push(li.cloneNode(true));
      });
      return clonedItems;
    }

    // Convert paragraph or div content to a list item
    var li = MochiKit.DOM.createDOM('li');
    while (block.firstChild) {
      li.appendChild(block.firstChild);
    }
    return [li];
  };
})();
