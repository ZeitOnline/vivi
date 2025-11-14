(function () {
  var Editable = zeit.content.article.Editable;

  // Orchestrates the conversion between paragraphs and lists (both directions).
  Editable.prototype._manual_toggle_list = function(listType) {
    var self = this;
    var selection = window.getSelection();
    if (!selection.rangeCount) {
      log('No selection for list toggle');
      return;
    }
    var range = selection.getRangeAt(0);
    var blocks = self._get_selected_blocks(range);
    if (blocks.length === 0) {
      return;
    }

    if (self._all_blocks_are_lists(blocks)) {
      self._convert_lists_to_paragraphs(blocks);
    } else {
      self._convert_blocks_to_list(blocks, listType, range);
    }
  };

  // Finds the block-level element (P, DIV, UL, OL) that is a direct child of
  // the editable container and contains the given node.
  Editable.prototype._find_editable_block = function(node) {
    var self = this;
    while (node && node !== self.editable) {
      if (self._is_block_element(node)) {
        return node;
      }
      node = node.parentNode;
    }
    return null;
  };

  // Checks if a node is a block element that can be converted to/from a list.
  // Only considers elements that are direct children of the editable container.
  Editable.prototype._is_block_element = function(node) {
    var self = this;
    if (node.parentNode !== self.editable) {
      return false;
    }
    var blockTypes = ['P', 'DIV', 'UL', 'OL'];
    return blockTypes.indexOf(node.nodeName) !== -1;
  };

  // Collects all block elements within the selection range.
  // This handles both single-block and multi-block selections.
  Editable.prototype._get_selected_blocks = function(range) {
    var self = this;
    var startContainer = range.startContainer;
    var endContainer = range.endContainer;

    // Text nodes need to be converted to their parent element nodes
    if (startContainer.nodeType === Node.TEXT_NODE) {
      startContainer = startContainer.parentNode;
    }
    if (endContainer.nodeType === Node.TEXT_NODE) {
      endContainer = endContainer.parentNode;
    }

    var startBlock = self._find_editable_block(startContainer);
    var endBlock = self._find_editable_block(endContainer);

    if (!startBlock || !endBlock) {
      log('Could not find start or end block');
      return [];
    }

    var blocks = [];
    var current = startBlock;
    while (current) {
      if (self._is_block_element(current)) {
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
  Editable.prototype._all_blocks_are_lists = function(blocks) {
    return blocks.every(function(block) {
      return block.nodeName === 'UL' || block.nodeName === 'OL';
    });
  };

  // All <li> items become a single <p> with <br> tags separating the former list items.
  // This is should be the same behaviour as calling the original command.
  Editable.prototype._convert_lists_to_paragraphs = function(blocks) {
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
  Editable.prototype._convert_blocks_to_list = function(blocks, listType, range) {
    var self = this;
    var list = MochiKit.DOM.createDOM(listType);
    var firstBlock = blocks[0];

    // Process each block and add it as a list item
    forEach(blocks, function(block) {
      var items = self._extract_list_items_from_block(block, listType);
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
  Editable.prototype._extract_list_items_from_block = function(block, listType) {
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
