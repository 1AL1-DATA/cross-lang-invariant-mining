#[derive(Debug, Clone, PartialEq)]
pub enum NestedList<T> {
    Element(T),
    List(Vec<NestedList<T>>),
}

impl<T> NestedList<T> {
    pub fn new_element(value: T) -> Self {
        NestedList::Element(value)
    }

    pub fn new_list(values: Vec<NestedList<T>>) -> Self {
        NestedList::List(values)
    }

    pub fn flatten(&self) -> Vec<T> {
        match self {
            NestedList::Element(value) => vec![value.clone()],
            NestedList::List(list) => {
                list.iter().flat_map(|item| item.flatten()).collect()
            }
        }
    }
}

pub fn flatten_a_list<T>(lst: &NestedList<T>) -> Vec<T> {
    lst.flatten()
}

impl<T> From<T> for NestedList<T> {
    fn from(value: T) -> Self {
        NestedList::Element(value)
    }
}